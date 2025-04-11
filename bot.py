import discord
import json
import os
from discord.ext import commands

# Load bot token from environment variable
TOKEN = os.getenv("TOKEN")
TARGET_CHANNEL_ID = 1346841725213212763  # Replace with your actual Discord channel ID
TALLY_FILE = "tally.json"  # File to store poop counts

# Load tally from file
def load_tally():
    try:
        with open(TALLY_FILE, "r") as file:
            data = json.load(file)
            print("🔄 Loaded existing tally data from file:", data)  # Debug log
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️ No previous tally found. Starting fresh.")
        return {}

# Save tally to file
def save_tally():
    print("🔹 Attempting to save tally...")  # Debug log
    try:
        with open(TALLY_FILE, "w") as file:
            json.dump(poop_tally, file, indent=4)
        print("✅ Tally saved successfully! Data:", poop_tally)  # Confirm save
    except Exception as e:
        print(f"❌ Failed to save tally: {e}")


# Dictionary to store count per user
poop_tally = load_tally()  # Load previous data when bot starts

# Setup bot
intents = discord.Intents.default()
intents.message_content = True  # Allow bot to read messages
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    print(f"📩 Message received from {message.author.name}: {message.content}")  # Debug log
    print(f"🔍 Raw message content: {repr(message.content)}")  # Shows exact format
    print(f"🏷️ Message Channel ID: {message.channel.id}")

    if message.author.bot:  # Ignore bot messages
        return

    if message.channel.id == TARGET_CHANNEL_ID:
        print("✅ Message is in the correct channel!")
        print(f"✅ Comparing '{message.content}' to '💩'")

        if "💩" in message.content:
            print("💩 Poop detected!")
            user_id = str(message.author.id)  # Convert to string for JSON storage
            previous_count = poop_tally.get(user_id, 0)
            poop_tally[user_id] = previous_count + message.content.count("💩")
            print(f"💩 Updated tally for {message.author.name}: {previous_count} → {poop_tally[user_id]}")
            print("📊 Current poop_tally:", poop_tally)  # Show full tally
            save_tally()  # Save after every update
            print("📁 Save function called!")

    await bot.process_commands(message)  # Allow commands to work



@bot.command()
async def tally(ctx):
    """Shows the current poop tally"""
    poop_tally = load_tally()  # Load updated data before displaying

    valid_users = {user_id: count for user_id, count in poop_tally.items() if count > 0}

    if not valid_users:  # If no users have sent poops, send only this message
        await ctx.send("No poop have been counted yet! 💩")
        return

    # If there are valid users, create the leaderboard
    tally_message = "**💩 Poop Leaderboard 💩**\n"
    for user_id, count in sorted(valid_users.items(), key=lambda x: x[1], reverse=True):
        user = await bot.fetch_user(int(user_id))  # Convert back to int
        tally_message += f"**{user.name}**: {count} 💩\n"

    # Send only ONE message
    await ctx.send(tally_message)

# Run bot
bot.run(TOKEN)
