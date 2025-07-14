import asyncio
import logging
import os
from pathlib import Path
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, SessionPasswordNeeded, PhoneCodeInvalid, PhoneNumberInvalid
from config import Config, temp
from database import db
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserBot:
    def __init__(self):
        self.api_id = Config.API_ID
        self.api_hash = Config.API_HASH
        self.phone = Config.PHONE_NUMBER
        
        # Create sessions directory
        os.makedirs(Config.SESSION_PATH, exist_ok=True)
        
        self.client = Client(
            name="userbot",
            api_id=self.api_id,
            api_hash=self.api_hash,
            workdir=Config.SESSION_PATH,
            plugins={"root": "plugins"}
        )
        
    async def start(self):
        """Start the userbot with authentication"""
        try:
            await self.client.start()
            me = await self.client.get_me()
            
            console.print(Panel(
                f"[green]✅ Userbot Started Successfully![/green]\n\n"
                f"[cyan]👤 Name:[/cyan] {me.first_name} {me.last_name or ''}\n"
                f"[cyan]📱 Phone:[/cyan] {me.phone_number}\n"
                f"[cyan]🆔 ID:[/cyan] {me.id}\n"
                f"[cyan]👤 Username:[/cyan] @{me.username or 'None'}",
                title="🤖 Userbot Status",
                border_style="green"
            ))
            
            temp.USER_CLIENT = self.client
            return self.client
            
        except SessionPasswordNeeded:
            console.print("[yellow]🔐 Two-factor authentication is enabled[/yellow]")
            password = Prompt.ask("Enter your 2FA password", password=True)
            await self.client.check_password(password)
            return await self.start()
            
        except Exception as e:
            console.print(f"[red]❌ Error starting userbot: {e}[/red]")
            raise

    async def stop(self):
        """Stop the userbot"""
        if self.client.is_connected:
            await self.client.stop()
            console.print("[yellow]🛑 Userbot stopped[/yellow]")

# Add userbot-specific handlers
@Client.on_message(filters.private & filters.command(["join"]))
async def join_channel(client, message):
    """Join a channel/group via invite link"""
    try:
        if len(message.command) < 2:
            return await message.reply(
                "**Usage:** `/join https://t.me/+invite_link`\n"
                "**Or:** `/join @channel_username`"
            )
        
        link_or_username = message.command[1]
        
        # Handle different link formats
        if link_or_username.startswith('https://t.me/+'):
            # Private invite link
            result = await client.join_chat(link_or_username)
        elif link_or_username.startswith('https://t.me/'):
            # Public channel link
            username = link_or_username.split('/')[-1]
            result = await client.join_chat(username)
        elif link_or_username.startswith('@'):
            # Username
            result = await client.join_chat(link_or_username)
        else:
            # Assume it's a username without @
            result = await client.join_chat(link_or_username)
        
        await message.reply(
            f"✅ **Successfully joined!**\n\n"
            f"**Chat:** {result.title}\n"
            f"**Type:** {result.type}\n"
            f"**Members:** {result.members_count if hasattr(result, 'members_count') else 'N/A'}"
        )
        
    except Exception as e:
        await message.reply(f"❌ **Error joining chat:** `{str(e)}`")

@Client.on_message(filters.private & filters.command(["leave"]))
async def leave_channel(client, message):
    """Leave a channel/group"""
    try:
        if len(message.command) < 2:
            return await message.reply(
                "**Usage:** `/leave @channel_username`\n"
                "**Or:** `/leave channel_id`"
            )
        
        chat_id = message.command[1]
        
        # Get chat info first
        chat = await client.get_chat(chat_id)
        
        # Leave the chat
        await client.leave_chat(chat_id)
        
        await message.reply(
            f"✅ **Successfully left!**\n\n"
            f"**Chat:** {chat.title}\n"
            f"**Type:** {chat.type}"
        )
        
    except Exception as e:
        await message.reply(f"❌ **Error leaving chat:** `{str(e)}`")

@Client.on_message(filters.private & filters.command(["mychats"]))
async def list_my_chats(client, message):
    """List all chats the userbot is member of"""
    try:
        chats_text = "**📋 Your Chats:**\n\n"
        
        async for dialog in client.get_dialogs():
            chat = dialog.chat
            if chat.type in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]:
                chat_type = "📢" if chat.type == enums.ChatType.CHANNEL else "👥"
                chats_text += f"{chat_type} **{chat.title}**\n"
                chats_text += f"   └ ID: `{chat.id}`\n"
                chats_text += f"   └ Username: @{chat.username or 'None'}\n\n"
        
        if len(chats_text) > 4000:
            # Split into multiple messages if too long
            parts = [chats_text[i:i+4000] for i in range(0, len(chats_text), 4000)]
            for part in parts:
                await message.reply(part)
        else:
            await message.reply(chats_text)
            
    except Exception as e:
        await message.reply(f"❌ **Error getting chats:** `{str(e)}`")

@Client.on_message(filters.private & filters.command(["chatinfo"]))
async def get_chat_info(client, message):
    """Get detailed information about a chat"""
    try:
        if len(message.command) < 2:
            return await message.reply(
                "**Usage:** `/chatinfo @channel_username`\n"
                "**Or:** `/chatinfo channel_id`"
            )
        
        chat_id = message.command[1]
        chat = await client.get_chat(chat_id)
        
        info_text = f"**📋 Chat Information:**\n\n"
        info_text += f"**Name:** {chat.title}\n"
        info_text += f"**ID:** `{chat.id}`\n"
        info_text += f"**Type:** {chat.type}\n"
        info_text += f"**Username:** @{chat.username or 'None'}\n"
        
        if hasattr(chat, 'members_count'):
            info_text += f"**Members:** {chat.members_count}\n"
        
        if hasattr(chat, 'description') and chat.description:
            info_text += f"**Description:** {chat.description[:100]}...\n"
        
        # Check if we can send messages
        try:
            permissions = await client.get_chat_member(chat.id, "me")
            info_text += f"**Your Status:** {permissions.status}\n"
        except:
            info_text += f"**Your Status:** Member\n"
        
        await message.reply(info_text)
        
    except Exception as e:
        await message.reply(f"❌ **Error getting chat info:** `{str(e)}`")