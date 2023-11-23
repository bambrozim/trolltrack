import os
import discord
from discord.ext import commands
from openai import OpenAI

bot_token = os.environ.get('BOT_TOKEN')
openai_apikey = os.environ.get('OPENAI_APIKEY')

# Define intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
# intents.presences = True  # Enable presence intent
# intents.guilds = True  # Enable server members intent

# Create an instance of the bot with intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Instance model for classifying toxic comments
client = OpenAI(api_key=openai_apikey)
model_gpt = 'gpt-3.5-turbo'

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Event handler for when a message is received
@bot.event
async def on_message(message):
    # Check if the message sender is the bot itself to avoid an infinite loop
    if message.author == bot.user:
        return

    # Check if the message starts with a specific command
    if message.content:
        # Respond with a greeting
        user_prompt = message.content

        system_judge_prompt = """You are a toxic comment classifier, you will receive a comment and judge if it is toxic
        or not. Your response must be in the format '<toxicity> | <language>', replacing <toxicity> with the word 'toxic' 
        if it is toxic or 'non-toxic' if it is not toxic, replace <language> with the language of the comment."""

        response_judge = client.chat.completions.create(
            model=model_gpt,
            messages=[
                {"role": "system", "content": system_judge_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        toxicity, language = response_judge.choices[0].message.content.split(' | ')

        if toxicity == 'toxic':

            system_pc_prompt = f"""Act like PC Principal character from South Park and, scold the person that made the 
            toxic comment, be humorous, concise (no more than 3 sentences) and use {language} idiom."""

            response_pc = client.chat.completions.create(
                model=model_gpt,
                messages=[
                    {"role": "system", "content": system_pc_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            await message.channel.send(f'{message.author.mention} {response_pc.choices[0].message.content}')


bot.run(bot_token)

