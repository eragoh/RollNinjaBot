import discord
from discord.ext import commands, tasks
import threading
import datetime
import asyncio
import time
utc = datetime.timezone.utc
t_time = datetime.time(hour=11, minute=19, tzinfo=utc)
print(t_time, utc)

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
        channel = self.get_channel(data["channels"]["poligon"]["id"])
        if channel:
            message = await channel.send('Panowie, kiedy sesja?')
            await message.add_reaction(emojis["Mon"])
            await message.add_reaction(emojis["Tu"])
            await message.add_reaction(emojis["Wed"])
            await message.add_reaction(emojis["Th"])
            await message.add_reaction(emojis["Fr"])
            await message.add_reaction(emojis["Sat"])
            await message.add_reaction(emojis["Sun"])
            await message.add_reaction(emojis["x"])
            await channel.send(" ".join(member.mention for member in channel.members if not member.bot))
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
        await asyncio.sleep(remaining_time)
        await self.wait_until_ready()


RollNinja = RollNinjaBot()
       
@RollNinja.command()
async def xd(ctx):
    print('xd')
    await ctx.send('xds')