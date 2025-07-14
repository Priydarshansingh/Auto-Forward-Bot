# 🤖 Telegram Auto Forward Bot - Local Setup Guide

## 📋 Prerequisites

### 1. Python Installation
- Install Python 3.8 or higher from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation

### 2. MongoDB Database
Choose one of these options:

#### Option A: MongoDB Atlas (Free Cloud Database) - **RECOMMENDED**
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a free account
3. Create a new cluster (free tier)
4. Get your connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

#### Option B: Local MongoDB
1. Install MongoDB Community Server from [mongodb.com](https://www.mongodb.com/try/download/community)
2. Use connection string: `mongodb://localhost:27017/`

### 3. Telegram API Credentials
1. Go to [my.telegram.org](https://my.telegram.org)
2. Login with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Note down your `API_ID` and `API_HASH`

## 🚀 Installation Steps

### Step 1: Download the Bot
```bash
# Clone or download this repository
git clone <repository-url>
cd telegram-auto-forward-bot
```

### Step 2: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### Step 3: Configuration
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your credentials:
   ```env
   # Get these from https://my.telegram.org
   API_ID=your_api_id_here
   API_HASH=your_api_hash_here

   # Your phone number with country code
   PHONE_NUMBER=+1234567890

   # MongoDB connection string
   DATABASE_URI=mongodb+srv://username:password@cluster.mongodb.net/
   DATABASE_NAME=forward-bot

   # Your Telegram User ID (get from @userinfobot)
   BOT_OWNER_ID=your_user_id
   ```

### Step 4: Run the Bot
```bash
python main.py
```

## 🎯 First Time Setup

### 1. Authentication
- When you first run the bot, it will ask for:
  - Phone number verification code
  - 2FA password (if enabled)

### 2. Join Source Channels
Use these commands to join channels:
```
/join https://t.me/+private_invite_link
/join @public_channel_username
/join https://t.me/channel_username
```

### 3. Setup Target Channels
1. Use `/settings` command
2. Add your target channels where converted links will be posted
3. Make sure your account is admin in target channels

### 4. Configure Chain Forwarding
1. Use `/chain` command
2. Forward a message from source channel
3. Enter converter bot username (e.g., `TeraBoxRobot`)
4. Select target channel
5. Done! The bot will now automatically handle the workflow

## 📱 Available Commands

### Chain Forwarding
- `/chain` - Setup automated forwarding workflow
- `/chainlist` - View current configuration
- `/chainon` - Enable chain forwarding
- `/chainoff` - Disable chain forwarding

### Channel Management
- `/join <link>` - Join channel/group via invite link
- `/leave <chat>` - Leave channel/group
- `/mychats` - List all your chats
- `/chatinfo <chat>` - Get detailed chat information

### Manual Forwarding
- `/forward` - Start manual forwarding process
- `/settings` - Configure bot settings

## 🔄 How Chain Forwarding Works

1. **Monitor** - Bot watches source channels for posts with convertible links
2. **Forward** - Automatically forwards to converter bot (e.g., @TeraBoxRobot)
3. **Wait** - Waits for converter bot's reply with modified links
4. **Post** - Automatically posts the result to your target channel

## 🛠️ Troubleshooting

### Common Issues

#### "Session file not found"
- This is normal on first run
- The bot will create a session file after authentication

#### "FloodWait" errors
- Telegram has rate limits
- The bot will automatically wait and retry

#### "Chat not found"
- Make sure you've joined the source channel
- Use `/join` command to join private channels

#### "Permission denied"
- Make sure your account is admin in target channels
- Check if you have necessary permissions

### Getting Help
- Check the console output for detailed error messages
- Look at the `bot.log` file for debugging information

## 🔒 Security Notes

- Keep your `.env` file secure and never share it
- Your session files contain sensitive data - don't share them
- Use strong 2FA on your Telegram account
- Only join trusted channels and use trusted converter bots

## 💡 Tips for Best Results

1. **Use a dedicated account** - Consider using a separate Telegram account for the bot
2. **Monitor logs** - Keep an eye on console output and log files
3. **Test first** - Try with a small test channel before using on important channels
4. **Backup settings** - Note down your configurations
5. **Stay updated** - Keep the bot code updated for new features and fixes

## 🎉 You're Ready!

Your bot is now configured and ready to automatically handle the TeraBox link conversion workflow. The bot will:

✅ Monitor your source channels  
✅ Auto-forward posts with links to converter bots  
✅ Wait for converted responses  
✅ Post final results to your channels  

Happy forwarding! 🚀