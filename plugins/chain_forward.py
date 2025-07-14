import asyncio
import re
import logging
import time
from database import db
from config import Config, temp
from translation import Translation
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import FloodWait
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)

# Store pending chain operations
CHAIN_OPERATIONS = {}

@Client.on_message(filters.private & filters.command(["chain", "chainforward"]))
async def setup_chain_forward(bot, message):
    """Setup chain forwarding configuration"""
    user_id = message.from_user.id
    
    # Check if userbot is available
    if not temp.USER_CLIENT:
        return await message.reply("❌ **Userbot not available!** Please restart the bot.")
    
    # Get user channels
    channels = await db.get_user_channels(user_id)
    if not channels:
        return await message.reply_text("Please set target channels in /settings before setting up chain forwarding")
    
    # Step 1: Get source channel
    source_msg = await bot.ask(
        message.chat.id, 
        "<b>❪ SET SOURCE CHANNEL ❫</b>\n\nForward a message from the source channel that posts TeraBox/similar links\n/cancel - cancel this process"
    )
    
    if source_msg.text and source_msg.text.startswith('/'):
        return await message.reply(Translation.CANCEL)
    
    if not source_msg.forward_from_chat:
        return await message.reply("Please forward a message from the source channel")
    
    source_chat_id = source_msg.forward_from_chat.id
    source_title = source_msg.forward_from_chat.title
    
    # Step 2: Get converter bot username
    converter_msg = await bot.ask(
        message.chat.id,
        "<b>❪ SET CONVERTER BOT ❫</b>\n\nSend the username of the converter bot (e.g., @TeraBoxRobot)\n/cancel - cancel this process"
    )
    
    if converter_msg.text.startswith('/'):
        return await message.reply(Translation.CANCEL)
    
    converter_bot = converter_msg.text.strip().replace('@', '')
    
    # Step 3: Select target channel
    if len(channels) > 1:
        buttons = []
        btn_data = {}
        for channel in channels:
            buttons.append([InlineKeyboardButton(f"{channel['title']}", callback_data=f"chain_target_{channel['chat_id']}")])
            btn_data[channel['chat_id']] = channel['title']
        
        buttons.append([InlineKeyboardButton("Cancel", callback_data="chain_cancel")])
        
        await message.reply(
            "<b>❪ CHOOSE TARGET CHANNEL ❫</b>\n\nSelect where to post the final converted links:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
        # Store temporary data
        temp.CHAIN_SETUP = temp.CHAIN_SETUP if hasattr(temp, 'CHAIN_SETUP') else {}
        temp.CHAIN_SETUP[user_id] = {
            'source_chat_id': source_chat_id,
            'source_title': source_title,
            'converter_bot': converter_bot,
            'channels': btn_data
        }
    else:
        target_chat_id = channels[0]['chat_id']
        target_title = channels[0]['title']
        
        # Save chain configuration
        await save_chain_config(user_id, source_chat_id, source_title, converter_bot, target_chat_id, target_title)
        
        await message.reply(
            f"<b>✅ Chain Forward Setup Complete!</b>\n\n"
            f"<b>Source:</b> {source_title}\n"
            f"<b>Converter:</b> @{converter_bot}\n"
            f"<b>Target:</b> {target_title}\n\n"
            f"The bot will now automatically:\n"
            f"1. Monitor {source_title} for new posts\n"
            f"2. Forward posts with links to @{converter_bot}\n"
            f"3. Wait for converted links\n"
            f"4. Post final result to {target_title}"
        )

@Client.on_callback_query(filters.regex(r'^chain_target_'))
async def handle_target_selection(bot, query):
    """Handle target channel selection"""
    user_id = query.from_user.id
    target_chat_id = int(query.data.split('_')[2])
    
    if not hasattr(temp, 'CHAIN_SETUP') or user_id not in temp.CHAIN_SETUP:
        return await query.answer("Setup expired. Please start again.", show_alert=True)
    
    setup_data = temp.CHAIN_SETUP[user_id]
    target_title = setup_data['channels'][target_chat_id]
    
    # Save chain configuration
    await save_chain_config(
        user_id,
        setup_data['source_chat_id'],
        setup_data['source_title'],
        setup_data['converter_bot'],
        target_chat_id,
        target_title
    )
    
    await query.message.edit_text(
        f"<b>✅ Chain Forward Setup Complete!</b>\n\n"
        f"<b>Source:</b> {setup_data['source_title']}\n"
        f"<b>Converter:</b> @{setup_data['converter_bot']}\n"
        f"<b>Target:</b> {target_title}\n\n"
        f"The bot will now automatically:\n"
        f"1. Monitor {setup_data['source_title']} for new posts\n"
        f"2. Forward posts with links to @{setup_data['converter_bot']}\n"
        f"3. Wait for converted links\n"
        f"4. Post final result to {target_title}"
    )
    
    # Clean up temporary data
    del temp.CHAIN_SETUP[user_id]

@Client.on_callback_query(filters.regex(r'^chain_cancel$'))
async def handle_chain_cancel(bot, query):
    """Handle chain setup cancellation"""
    user_id = query.from_user.id
    if hasattr(temp, 'CHAIN_SETUP') and user_id in temp.CHAIN_SETUP:
        del temp.CHAIN_SETUP[user_id]
    
    await query.message.edit_text("Chain forward setup cancelled.")

async def save_chain_config(user_id, source_chat_id, source_title, converter_bot, target_chat_id, target_title):
    """Save chain forwarding configuration to database"""
    chain_config = {
        'user_id': user_id,
        'source_chat_id': source_chat_id,
        'source_title': source_title,
        'converter_bot': converter_bot,
        'target_chat_id': target_chat_id,
        'target_title': target_title,
        'active': True
    }
    
    # Add to database (you might need to create a new collection for this)
    await db.db.chain_configs.replace_one(
        {'user_id': user_id},
        chain_config,
        upsert=True
    )

@Client.on_message(filters.channel)
async def monitor_source_channels(bot, message):
    """Monitor source channels for new posts with links"""
    try:
        # Only process if this is from userbot
        if not temp.USER_CLIENT or bot != temp.USER_CLIENT:
            return
            
        # Get all active chain configurations
        chain_configs = await db.db.chain_configs.find({'active': True}).to_list(None)
        
        for config in chain_configs:
            if message.chat.id == config['source_chat_id']:
                # Check if message contains links
                if has_convertible_links(message):
                    await process_chain_forward(bot, message, config)
                    
    except Exception as e:
        logger.error(f"Error in monitor_source_channels: {e}")

def has_convertible_links(message):
    """Check if message contains convertible links (TeraBox, etc.)"""
    if not message.text and not message.caption:
        return False
    
    text = message.text or message.caption
    
    # Common file sharing domains that might need conversion
    convertible_domains = [
        'terabox.com',
        'teraboxapp.com', 
        '1024tera.com',
        'nephobox.com',
        'freeterabox.com',
        'terabox.app',
        'teraboxlink.com',
        'mirrobox.com',
        'momerybox.com',
        'teraboxs.com',
        'tibibox.com',
        '4funbox.co',
        'terasharelink.com'
    ]
    
    # Check for any convertible links
    for domain in convertible_domains:
        if domain in text.lower():
            return True
    
    return False

async def process_chain_forward(bot, original_message, config):
    """Process the chain forwarding operation"""
    try:
        user_id = config['user_id']
        converter_bot = config['converter_bot']
        target_chat_id = config['target_chat_id']
        
        # Use the userbot client
        if not temp.USER_CLIENT:
            logger.error(f"Userbot not available for user {user_id}")
            return
        
        user_client = temp.USER_CLIENT
        
        # Step 1: Forward original message to converter bot
        console.print(f"[cyan]🔄 Forwarding message to @{converter_bot}[/cyan]")
        forwarded_msg = await user_client.forward_messages(
            chat_id=converter_bot,
            from_chat_id=original_message.chat.id,
            message_ids=original_message.id
        )
        
        # Step 2: Wait for converter bot reply
        operation_id = f"{user_id}_{original_message.id}_{forwarded_msg.id}"
        CHAIN_OPERATIONS[operation_id] = {
            'user_client': user_client,
            'original_message': original_message,
            'target_chat_id': target_chat_id,
            'converter_bot': converter_bot,
            'forwarded_msg_id': forwarded_msg.id,
            'timestamp': time.time(),
            'user_id': user_id
        }
        
        # Set up timeout (5 minutes)
        asyncio.create_task(cleanup_operation(operation_id, 300))
        
        console.print(f"[green]✅ Chain operation started: {operation_id}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error in process_chain_forward: {e}[/red]")

@Client.on_message(filters.private)
async def handle_converter_replies(bot, message):
    """Handle replies from converter bots"""
    try:
        # Only process if this is from userbot
        if not temp.USER_CLIENT or bot != temp.USER_CLIENT:
            return
            
        if not message.reply_to_message:
            return
        
        # Find matching chain operation
        for operation_id, operation in CHAIN_OPERATIONS.items():
            if (message.chat.username == operation['converter_bot'] and 
                message.reply_to_message.id == operation['forwarded_msg_id']):
                
                console.print(f"[cyan]📤 Posting converted result to target channel[/cyan]")
                
                # Step 3: Forward the converted reply to target channel
                await operation['user_client'].copy_message(
                    chat_id=operation['target_chat_id'],
                    from_chat_id=message.chat.id,
                    message_id=message.id
                )
                
                console.print(f"[green]✅ Chain operation completed: {operation_id}[/green]")
                
                # Clean up (don't stop the client, just remove from operations)
                del CHAIN_OPERATIONS[operation_id]
                break
                
    except Exception as e:
        console.print(f"[red]❌ Error in handle_converter_replies: {e}[/red]")

async def cleanup_operation(operation_id, timeout):
    """Clean up chain operation after timeout"""
    await asyncio.sleep(timeout)
    
    if operation_id in CHAIN_OPERATIONS:
        del CHAIN_OPERATIONS[operation_id]
        console.print(f"[yellow]⏰ Chain operation timed out: {operation_id}[/yellow]")

@Client.on_message(filters.private & filters.command(["chainlist"]))
async def list_chain_configs(bot, message):
    """List active chain configurations"""
    user_id = message.from_user.id
    
    config = await db.db.chain_configs.find_one({'user_id': user_id})
    
    if not config:
        return await message.reply("No chain forwarding configured. Use /chain to set up.")
    
    status = "✅ Active" if config['active'] else "❌ Inactive"
    
    await message.reply(
        f"<b>🔗 Chain Forward Configuration</b>\n\n"
        f"<b>Status:</b> {status}\n"
        f"<b>Source:</b> {config['source_title']}\n"
        f"<b>Converter:</b> @{config['converter_bot']}\n"
        f"<b>Target:</b> {config['target_title']}\n\n"
        f"Use /chainoff to disable or /chain to reconfigure."
    )

@Client.on_message(filters.private & filters.command(["chainoff"]))
async def disable_chain_forward(bot, message):
    """Disable chain forwarding"""
    user_id = message.from_user.id
    
    result = await db.db.chain_configs.update_one(
        {'user_id': user_id},
        {'$set': {'active': False}}
    )
    
    if result.modified_count > 0:
        await message.reply("✅ Chain forwarding disabled.")
    else:
        await message.reply("No active chain forwarding found.")

@Client.on_message(filters.private & filters.command(["chainon"]))
async def enable_chain_forward(bot, message):
    """Enable chain forwarding"""
    user_id = message.from_user.id
    
    result = await db.db.chain_configs.update_one(
        {'user_id': user_id},
        {'$set': {'active': True}}
    )
    
    if result.modified_count > 0:
        await message.reply("✅ Chain forwarding enabled.")
    else:
        await message.reply("No chain forwarding configuration found. Use /chain to set up.")