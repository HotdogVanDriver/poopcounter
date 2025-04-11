import discord
import json
import os
import random
from discord.ext import commands

# Load bot token from environment variable
TOKEN = os.getenv("TOKEN")
TARGET_CHANNEL_ID = 1346841725213212763  # Replace with your actual Discord channel ID

# Load tally from environment variable
def load_tally():
    try:
        data = os.getenv("TALLY_DATA")
        if data:
            tally = json.loads(data)
            print("🔄 Loaded tally from TALLY_DATA env var:", tally)
            return tally
        else:
            print("⚠️ No TALLY_DATA found, starting fresh.")
            return {}
    except Exception as e:
        print(f"❌ Failed to load tally from env var: {e}")
        return {}

# Save tally to logs (manual copy/paste for Railway)
def save_tally():
    print("📦 Updated tally — paste this into Railway TALLY_DATA if needed:")
    print(json.dumps(poop_tally, indent=2))

# Milestone messages
milestone_messages = [
    "🎉 {name} just dropped their {count}th poop! Do you even wipe, bro?",
    "💩 {name} has gone {count} times. We're gonna need a bigger toilet.",
    "🚽 {name} unlocked the {count}-poop badge! That's commitment.",
    "🔥 {name} is on a poop streak! {count} poops and counting!",
    "🧻 Someone get {name} some toilet paper. That's {count} 💩 now!",
    "🥵 {name} hit {count} dumps. Somebody call a plumber!"
]

# Dictionary to store count per user
poop_tally = load_tally()

# Setup bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore other bots (including itself)

    # Don't process poop logic for command messages
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    print(f"📩 Message received from {message.author.name}: {message.content}")
    print(f"🔍 Raw message content: {repr(message.content)}")
    print(f"🏷️ Message Channel ID: {message.channel.id}")

    if message.channel.id == TARGET_CHANNEL_ID:
        print("✅ Message is in the correct channel!")
        print(f"✅ Comparing '{message.content}' to '💩'")

        if "💩" in message.content:
            print("💩 Poop detected!")
            user_id = str(message.author.id)
            previous_count = poop_tally.get(user_id, 0)
            poop_tally[user_id] = previous_count + message.content.count("💩")
            print(f"💩 Updated tally for {message.author.name}: {previous_count} → {poop_tally[user_id]}")
            print("📊 Current poop_tally:", poop_tally)
            save_tally()

            # 🎉 Milestone celebration
            if poop_tally[user_id] % 10 == 0:
                msg = random.choice(milestone_messages)
                await message.channel.send(msg.format(name=message.author.display_name, count=poop_tally[user_id]))

    await bot.process_commands(message)

@bot.command()
async def tally(ctx):
    print("⚙️ !tally command triggered")

    valid_users = {user_id: count for user_id, count in poop_tally.items() if count > 0}

    if not valid_users:
        await ctx.send("No poop emojis have been counted yet! 💩")
        return

    tally_message = "**💩 Poop Emoji Leaderboard 💩**\n"
    for user_id, count in sorted(valid_users.items(), key=lambda x: x[1], reverse=True):
        try:
            user = await bot.fetch_user(int(user_id))
            tally_message += f"**{user.name}**: {count} 💩\n"
        except:
            tally_message += f"**Unknown User ({user_id})**: {count} 💩\n"

    await ctx.send(tally_message)
    print("✅ Leaderboard sent.")

# Run the bot
bot.run(TOKEN)
