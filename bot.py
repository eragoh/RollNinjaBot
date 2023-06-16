import discord
from discord.ext import commands, tasks
import datetime
import asyncio
from random import randint

from json_data import data, emojis

class RollNinjaBot(commands.Bot):
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)

    def fight(self, token):
        self.run(token)

    async def on_ready(self):
        print(f"We have logged in as {self.user}")

    async def setup_hook(self):
        self.reminder.start()

    async def on_message(self, message):
        if message.content.startswith('!'):
            await self.process_commands(message)
            return
        if message.author == self.user:
            return
        
        print(message)
        print(message.content)
    
    @tasks.loop(seconds=data["reminder_time"])
    async def reminder(self):
        channel_name = 'artefakt-rpg'
        #channel_name = 'poligon'
        channel = self.get_channel(data["channels"][channel_name]["id"])
        
        if channel:
            message = await channel.send(f'# Drodzy gracze! Kiedy możecie w tym tygodniu grać w <@&{data["channels"][channel_name]["role"]}>?')
            await message.add_reaction(emojis["Mon"])
            await message.add_reaction(emojis["Tu"])
            await message.add_reaction(emojis["Wed"])
            await message.add_reaction(emojis["Th"])
            await message.add_reaction(emojis["Fr"])
            await message.add_reaction(emojis["Sat"])
            await message.add_reaction(emojis["Sun"])
            await message.add_reaction(emojis["x"])
            #await channel.send(" ".join(member.mention for member in channel.members if not member.bot))
        else:
            print('Channel not found')

    @reminder.before_loop
    async def before_reminder(self):
        target_time = datetime.time(9, 0)
        current_day = datetime.datetime.now().date().weekday()
        days_until_sunday = (6 - current_day) % 7
        next_sunday = datetime.datetime.now() + datetime.timedelta(days=days_until_sunday)
        next_sunday = next_sunday.replace(hour=target_time.hour, minute=target_time.minute)
        remaining_time = int((next_sunday - datetime.datetime.now()).total_seconds())
        #remaining_time = 1
        await asyncio.sleep(remaining_time)
        await self.wait_until_ready()

RollNinja = RollNinjaBot()
       
@RollNinja.command()
async def xd(ctx):
    await ctx.send('Chciałbyś')

@RollNinja.command()
async def roll(ctx):
    try:
        message = ctx.message.content.split(' ')[1]
        n, k = message.split('k')
        n, k = int(n) if n else 1, int(k)
        if n > 200 or k > 1000:
            raise Exception('No chyba zwariowałeś!')
        l = [randint(1, k) for _ in range(n)]
        s = f'Wynik rzutu **{n}k{k}** = {", ".join(str(ll) for ll in l)} | Suma = {sum(l)}'
        await ctx.send(s)
    except Exception as e:
        await ctx.send(f'Co ty wyrabiasz panie??? ({e})')

@RollNinja.command()
async def r(ctx):
    await roll(ctx)

@RollNinja.command()
async def days(ctx):
    await ctx.send("""
*Poniedziałek:* :coffee: 
*Wtorek:* :smile:
*Środa:* :camel: 
*Czwartek:* :raised_hands:
*Piątek:* :tada: 
*Sobota:* :partying_face: 
*Niedziela:* :sun_with_face:
*Nie mogę w tym tygodniu:* :x:
    """)