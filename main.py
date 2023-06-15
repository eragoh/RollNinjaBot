import discord
from discord.ext import commands

token = 'token'

intents = discord.Intents.default()

# create instance of bot
bot = commands.Bot(command_prefix='!', intents=intents)

# bot event on_ready
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# command xd
@bot.command()
async def xd(ctx):
    await ctx.send('xd')

# run the bot with your token
bot.run(token)
