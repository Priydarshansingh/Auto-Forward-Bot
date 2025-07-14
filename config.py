import os
from decouple import config

class Config:
    # Get from https://my.telegram.org
    API_ID = config("API_ID", cast=int)
    API_HASH = config("API_HASH")
    
    # Get from @BotFather (optional - for bot features)
    BOT_TOKEN = config("BOT_TOKEN", default="")
    BOT_SESSION = config("BOT_SESSION", default="bot")
    
    # Your Telegram Phone Number (for userbot)
    PHONE_NUMBER = config("PHONE_NUMBER", default="")
    
    # MongoDB Database (you can use MongoDB Atlas free tier or local MongoDB)
    DATABASE_URI = config("DATABASE_URI")
    DATABASE_NAME = config("DATABASE_NAME", default="forward-bot")
    
    # Your Telegram User ID (get from @userinfobot)
    BOT_OWNER_ID = [int(id) for id in config("BOT_OWNER_ID", default="").split(",") if id.strip()]
    
    # Session file path
    SESSION_PATH = config("SESSION_PATH", default="./sessions/")

class temp(object): 
    lock = {}
    CANCEL = {}
    forwardings = 0
    BANNED_USERS = []
    IS_FRWD_CHAT = []
    CHAIN_SETUP = {}
    USER_CLIENT = None  # Store user client globally