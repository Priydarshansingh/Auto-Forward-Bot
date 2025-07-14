#!/usr/bin/env python3
import asyncio
import logging
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from userbot import UserBot
from config import Config
from database import db

console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_config():
    """Check if all required configuration is present"""
    missing = []
    
    if not Config.API_ID:
        missing.append("API_ID")
    if not Config.API_HASH:
        missing.append("API_HASH")
    if not Config.DATABASE_URI:
        missing.append("DATABASE_URI")
    
    if missing:
        console.print(Panel(
            f"[red]❌ Missing required configuration:[/red]\n\n" +
            "\n".join([f"• {item}" for item in missing]) +
            f"\n\n[yellow]Please check your .env file![/yellow]",
            title="⚠️ Configuration Error",
            border_style="red"
        ))
        return False
    
    return True

async def main():
    """Main function to run the userbot"""
    try:
        # Show welcome message
        console.print(Panel(
            Text.from_markup(
                "[bold blue]🤖 Telegram Auto Forward Bot[/bold blue]\n"
                "[cyan]Chain Forwarding Edition[/cyan]\n\n"
                "[green]✨ Features:[/green]\n"
                "• Auto-forward with link conversion\n"
                "• Join channels via invite links\n"
                "• Monitor private channels\n"
                "• TeraBox link conversion\n"
                "• And much more!"
            ),
            title="🚀 Welcome",
            border_style="blue"
        ))
        
        # Check configuration
        if not check_config():
            return
        
        # Initialize and start userbot
        console.print("[cyan]🔄 Starting userbot...[/cyan]")
        userbot = UserBot()
        await userbot.start()
        
        # Show available commands
        console.print(Panel(
            "[bold green]📋 Available Commands:[/bold green]\n\n"
            "[cyan]Chain Forwarding:[/cyan]\n"
            "• /chain - Setup automated forwarding\n"
            "• /chainlist - View configurations\n"
            "• /chainon - Enable chain forwarding\n"
            "• /chainoff - Disable chain forwarding\n\n"
            "[cyan]Channel Management:[/cyan]\n"
            "• /join <link> - Join channel/group\n"
            "• /leave <chat> - Leave channel/group\n"
            "• /mychats - List your chats\n"
            "• /chatinfo <chat> - Get chat info\n\n"
            "[cyan]Forwarding:[/cyan]\n"
            "• /forward - Manual forwarding\n"
            "• /settings - Configure settings",
            title="🎯 Commands",
            border_style="green"
        ))
        
        console.print("[green]✅ Bot is running! Send commands to your userbot.[/green]")
        console.print("[yellow]💡 Tip: Use /join <invite_link> to join private channels[/yellow]")
        console.print("[red]🛑 Press Ctrl+C to stop[/red]")
        
        # Keep the bot running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]🛑 Bot stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        logger.error(f"Error in main: {e}")
    finally:
        try:
            await userbot.stop()
        except:
            pass

if __name__ == "__main__":
    # Check if .env file exists
    if not os.path.exists('.env'):
        console.print(Panel(
            "[red]❌ .env file not found![/red]\n\n"
            "[yellow]Please create a .env file with your credentials.[/yellow]\n"
            "[cyan]Check .env.example for reference.[/cyan]",
            title="⚠️ Setup Required",
            border_style="red"
        ))
        sys.exit(1)
    
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]💥 Fatal error: {e}[/red]")
        logger.error(f"Fatal error: {e}")