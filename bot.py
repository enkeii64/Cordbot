import discord
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not DISCORD_TOKEN or not GEMINI_API_KEY:
    raise ValueError("DISCORD_TOKEN or GEMINI_API_KEY not set. Please check your .env file.")

genai.configure(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.messages = True
discord_client = discord.Client(intents=intents)

DATA_FILE = "knowledge_data.json"
data = {
    "general_knowledge": [],
    "response_knowledge": [],
    "config_allowed_users": ["enkei2"]  # Default admin user - enter your Discord username if you are the owner (configurator) of the bot.
}

gemini_usage = {"messages_sent": 0, "tokens_used": 0}

response_queue = {}

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print("JSON file corrupted. Creating a new one.")
            with open(DATA_FILE, "w") as reset_file:
                json.dump(data, reset_file, indent=4)
else:
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def save_data():
    """Persist the current state of the data to a JSON file."""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Utility function: Format knowledge with indices
def format_knowledge(knowledge):
    """Format a list of knowledge entries with numbers."""
    return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(knowledge)) if knowledge else "No entries available."

def split_response(content, max_length=1900):
    """Split a response into chunks that fit within Discord's message limits."""
    parts = []
    while len(content) > max_length:
        split_at = content[:max_length].rfind("\n")
        if split_at == -1:
            split_at = max_length
        parts.append(content[:split_at].strip())
        content = content[split_at:].strip()
    if content:
        parts.append(content)
    return parts

def is_config_allowed(user: discord.User) -> bool:
    """Determine if a user has permission to modify bot configurations."""
    return user.name in data["config_allowed_users"]

async def process_query(message, user_query):
    """
    Process user queries using the Gemini API and manage multi-part responses.
    """
    system_prompt = (
        "REPLACE ME WITH WHAT THE BOT IS - TELL THE BOT WHAT IT IS"
        "Your responses must be relevant, concise, and free from unnecessary technical references like '(knowledge base item X)'. "
        "Do not include unrelated instructions unless explicitly requested by the user. "
        f"Here is your knowledge base:\n\n"
        f"General Knowledge:\n{format_knowledge(data['general_knowledge'])}\n" # DO NOT REMOVE THIS, IT IS THE CONNECTION OF THE SYSTEM PROMPT TO THE GENERAL KNOWLEDGE
        f"Response Knowledge:\n{format_knowledge(data['response_knowledge'])}\n\n" # DO NOT REMOVE THIS, IT IS THE CONNECTION OF THE SYSTEM PROMPT TO THE RESPONSE KNOWLEDGE
        "YOU CAN ADD MORE SYSTEM PROMPTS THROUGH ADDING NEW LINES WITH PROMPTS IN DOUBLE QUOTATION MARKS."
    )

    prompt = f"{system_prompt}\n\nUser: {user_query}"
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        gemini_usage["messages_sent"] += 1
        gemini_usage["tokens_used"] += len(response.text)

        response_parts = split_response(response.text.strip())
        for part in response_parts:
            await message.reply(part)

    except Exception as e:
        await message.reply(f"Sorry, I couldn't process your request at the moment. Error: {str(e)}")
        print(f"Error: {str(e)}")

async def handle_command(message, content):
    """
    Parse and execute bot commands issued by users.
    """
    global response_queue

    # View settings menu
    if content.lower() == "settings":
        settings_menu = (
            "**Settings Menu**\n"
            "Commands:\n"
            "- **Add general knowledge**: @Cordbot gk add ...\n"
            "- **Add response knowledge**: @Cordbot AI rk add ...\n"
            "- **Remove general knowledge**: @Cordbot AI gk remove {number}\n"
            "- **Remove response knowledge**: @Cordbot AI rk remove {number}\n"
            "- **View General Knowledge**: @Cordbot AI gk view\n"
            "- **View Response Knowledge**: @Cordbot AI rk view\n"
            "- **Allow someone to config**: @Cordbot config y {username}\n"
            "- **Remove someone's ability to config**: @Cordbot config n {username}\n"
            "- **Gemini Usage Info**: @Cordbot AI gemini\n"
            "- **Continue response**: @Cordbot AI continue\n"
            "- **Continue all response**: @Cordbot AI continue all\n"
            "Note: owner (replace me in code) always has config access and cannot be removed."
        )
        await message.reply(settings_menu)
        return

    if content.lower() == "gemini":
        usage_info = (
            f"**Gemini Usage Info**\n"
            f"- Messages sent since startup: {gemini_usage['messages_sent']}\n"
            f"- Tokens used since startup: {gemini_usage['tokens_used']}\n"
        )
        await message.reply(usage_info)
        return

    if content.lower() == "gk view":
        chunks = split_response(format_knowledge(data["general_knowledge"]))
        if chunks:
            for chunk in chunks:
                await message.reply(chunk)
        else:
            await message.reply("**General Knowledge:**\nNo entries available.")
        return

    if content.lower() == "rk view":
        chunks = split_response(format_knowledge(data["response_knowledge"]))
        if chunks:
            for chunk in chunks:
                await message.reply(chunk)
        else:
            await message.reply("**Response Knowledge:**\nNo entries available.")
        return

    if content.startswith("gk add ") or content.startswith("rk add "):
        if not is_config_allowed(message.author):
            await message.reply("You don't have permission to modify the knowledge base.")
            return

        knowledge_type = "general" if content.startswith("gk add ") else "response"
        knowledge = content[7:].strip()

        if knowledge_type == "general":
            data["general_knowledge"].append(knowledge)
        else:
            data["response_knowledge"].append(knowledge)

        save_data()
        await message.reply(f"{knowledge_type.capitalize()} knowledge added: {knowledge}")
        return

    if content.startswith("gk remove ") or content.startswith("rk remove "):
        if not is_config_allowed(message.author):
            await message.reply("You don't have permission to modify the knowledge base.")
            return

        knowledge_type = "general" if content.startswith("gk remove ") else "response"
        try:
            index = int(content[len(f"{knowledge_type} remove "):].strip()) - 1
            if 0 <= index < len(data[f"{knowledge_type}_knowledge"]):
                removed_item = data[f"{knowledge_type}_knowledge"].pop(index)
                save_data()
                await message.reply(f"Removed from {knowledge_type} knowledge: {removed_item}")
            else:
                await message.reply(f"Invalid number. Use the command @Cordbot {knowledge_type} view to see the correct indices.")
        except ValueError:
            await message.reply("Invalid input. Please provide a valid number.")
        return

    await message.reply("Invalid command. Type @Cordbot AI settings for a list of valid commands.")

@discord_client.event
async def on_ready():
    print(f"Logged in as {discord_client.user}")

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    mentioned = discord_client.user.mentioned_in(message)
    replied_to_bot = message.reference and message.reference.resolved and message.reference.resolved.author == discord_client.user

    if not mentioned and not replied_to_bot:
        return

    content = message.content.strip()
    if mentioned:
        content = content.replace(f"<@{discord_client.user.id}>", "").strip()

    if content.lower().startswith((
        "settings", "gemini", "gk add", "rk add", "gk remove", "rk remove", "gk view", "rk view"
    )):
        await handle_command(message, content)
    else:
        await process_query(message, content)

discord_client.run(DISCORD_TOKEN)