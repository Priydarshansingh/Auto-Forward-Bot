import os
from decouple import config

class Config:
    # Get from https://my.telegram.org
    API_ID = config("API_ID", cast=int)
    API_HASH = config("API_HASH")
    
    # Get from @BotFather
    BOT_TOKEN = config("BOT_TOKEN")
    BOT_SESSION = config("BOT_SESSION", default="bot")
    
    # MongoDB Database (you can use MongoDB Atlas free tier)
    DATABASE_URI = config("DATABASE_URI")
    DATABASE_NAME = config("DATABASE_NAME", default="forward-bot")
    
    # Your Telegram User ID (get from @userinfobot)
    BOT_OWNER_ID = [int(id) for id in config("BOT_OWNER_ID", default="").split(",") if id.strip()]

class temp(object): 
    lock = {}
    CANCEL = {}
    forwardings = 0
    BANNED_USERS = []
    IS_FRWD_CHAT = []
    CHAIN_SETUP = {}