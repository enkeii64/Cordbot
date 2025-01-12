# Cordbot Setup Guide

## Overview
Cordbot is a customizable Discord bot powered by Google Gemini AI. It processes user queries, manages a knowledge base, and provides various useful commands. It’s designed to run continuously and can be integrated into any Discord server.

## Prerequisites
Before setting up the bot, make sure you have the following:

Python 3.11+ installed on your machine.
A Discord account and a Discord bot token.
A Google Gemini API key (or any API you want to use for processing user queries).

# Step-by-Step Setup
## 1. Clone the Repository
Clone the repository to your local machine:

```
git clone https://github.com/enkei64/Cordbot
cd your-repo-directory
```

## 2. Set Up Python Virtual Environment
It’s recommended to use a virtual environment to manage dependencies.

Install virtualenv (if not already installed):

```
pip install virtualenv
```

Create a virtual environment:

```
python3.11 -m venv venv
```

Activate the virtual environment:

### On macOS/Linux:

```
source venv/bin/activate
```
### On Windows:

```
.\venv\Scripts\activate
```

## 3. Install Required Dependencies
Install all required Python dependencies by running:

```
pip install -r requirements.txt
```

## 4. Create a .env File
Create a .env file in the root directory of your project to store sensitive environment variables like your Discord bot token and API key.

### Example .env file:
```
DISCORD_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

## 5. Modify the System Prompt (Optional)
## To modify the system’s behavior, adjust the system_prompt in the code. This string controls how the bot generates responses to user queries.

### Find this section in the code:

```
system_prompt = (
    "You are NuggetSupportAI, a support bot that uses a knowledge base to help users troubleshoot their problems."
    # Modify the prompt as needed
)
```

Change it to reflect your desired functionality.

## 6. Running the Bot
To run the bot, make sure the virtual environment is active and then execute the following command:

```
python bot.py
```
Your bot should now be running and connected to your Discord server.

## Bot Commands
Here are the available commands for the bot:
```
settings: Displays a list of all available commands.
gemini: Shows the Gemini usage stats (messages sent, tokens used).
gk add <message>: Adds a general knowledge item to the bot’s memory.
rk add <message>: Adds a response knowledge item.
gk remove <index>: Removes a general knowledge item based on the index number.
rk remove <index>: Removes a response knowledge item.
gk view: Displays all general knowledge items.
rk view: Displays all response knowledge items.
```

## Troubleshooting
### If you encounter issues, ensure your .env file contains the correct API keys, and that your virtual environment is properly set up.

## License

This project is licensed under the Apache License 2.0, with the following modifications:

- You are free to edit, modify, and redistribute the code as long as the modified code is not used or resold for commercial purposes.
- This work is only allowed for **non-commercial** purposes unless explicit written permission is granted by the author for commercial use.

For more details, see the [LICENSE](LICENSE) file.

