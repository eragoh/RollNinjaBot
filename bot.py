import discord
from discord.ext import commands, tasks
import datetime
import asyncio
from random import randint, choice
import json

from log import log, logc, logf, logger
import dbs.db_funcs as dbf

with open('data/emoji.json', 'r') as f:
    emojis = json.loads(f.read())
def info(type, user, message):
    logger.debug(f'{type} - {user} - {message}')

class RollNinjaBot(commands.Bot):
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)

    def fight(self, token):
        logger.debug('function fight called')
        self.run(token)

    @log
    async def on_ready(self):
        print(f"Logged in as {self.user}")

    @log
    async def setup_hook(self):
        self.reminder.start()
        self.remind_late_players.start()

    async def on_message(self, message):
        if message.content.startswith('!'):
            await self.process_commands(message)
            return
        if message.author == self.user:
            return
        
        #print(message)
        #print(message.content)
    
    @tasks.loop(seconds=dbf.db_get_value('reminder_time'))
    async def reminder(self):
        logf('reminder')
        channels = dbf.db_channels()
        for channel_name in channels:
            ch = channels[channel_name]
            id = ch['id']
            role = ch['role']
            channel = self.get_channel(id)

            message = await channel.send(f'# Drodzy gracze! Kiedy możecie w tym tygodniu grać w <@&{role}>?')
            for em in ["Mon", "Tu", "Wed", "Th", "Fr", "Sat", "Sun", "x"]:
                await message.add_reaction(emojis[em])
            dbf.db_set_last_message(channel_name, message.id)
            

    @reminder.before_loop
    async def before_reminder(self):
        target_time = datetime.time(9, 0)
        current_day = datetime.datetime.now().date().weekday()
        days_until_sunday = (6 - current_day) % 7
        next_sunday = datetime.datetime.now() + datetime.timedelta(days=days_until_sunday)
        next_sunday = next_sunday.replace(hour=target_time.hour, minute=target_time.minute)
        remaining_time = int((next_sunday - datetime.datetime.now()).total_seconds())
        #remaining_time = 1
        logger.info(f"function 'before_reminder' set delay time to: {remaining_time}s")
        await asyncio.sleep(remaining_time)
        await self.wait_until_ready()

    @tasks.loop(seconds=dbf.db_get_value('reminder_to_reminder_time'))
    async def remind_late_players(self):
        logf('remind_late_players')
        channels = dbf.db_channels()
        for channel_name in channels:
            ch = channels[channel_name]
            id = ch['id']
            channel = self.get_channel(id)
            message_id = dbf.db_get_last_message(str(channel))
            try:
                message = await channel.fetch_message(int(message_id))
                if not message:
                    raise Exception(f'Not message found // remind_late_players / {channel_name}')
            except:
                return
            
            guild = self.get_guild(dbf.db_get_value('guild'))
            role = discord.utils.get(guild.roles, id=ch["role"])
            users = set()
            members = set()
            for r in message.reactions:
                async for user in r.users():
                    users.add(user)
            for member in channel.members:
                if role in member.roles:
                    if not member in users:
                        members.add(member)
            if members:
                remind_users = ' '.join(f'{member.mention}' for member in members)
                reminder_message = dbf.db_get_quotes('reminders').replace('[user]', f'{remind_users}')
                await message.reply(reminder_message)

    @remind_late_players.before_loop
    async def before_remind_late_players(self):
        t = datetime.datetime.now()
        remaining_time = (59  - t.minute) * 60 + 60 - t.second
        #remaining_time = 10
        logger.info(f"function 'before_remind_late_players' set delay time to: {remaining_time}s")
        await asyncio.sleep(remaining_time)
        await self.wait_until_ready()

RollNinja = RollNinjaBot()

@RollNinja.command()
async def xd(ctx):
    """Sam zobacz xD"""
    logc('xd', ctx=ctx)
    quote = dbf.db_get_quotes('xd')
    await ctx.send(quote)

@RollNinja.command()
async def roll(ctx):
    """Rzut kośćmi w formacie mkn, np. 10k100"""
    try:    
        message = ctx.message.content.split(' ')[1]
        logc('roll', message, ctx=ctx)

        n, k = message.split('k')
        n, k = int(n) if n else 1, int(k)
        if n > 200 or k > 1000:
            raise Exception('No chyba zwariowałeś! (max 200k1000)')
        max_p, min_p = int(0.95 * k), int(0.05 * k) + 1
        
        l = [
            randint(1, k) 
            for _ in range(n)
        ]

        results = [
            str(ll) if ll <= max_p and ll > min_p else f"**{ll}**" 
            for ll in l
        ]

        s = f'Wynik rzutu **{n}k{k}** = {", ".join(results)} | Suma = {sum(l)}'
        await ctx.send(s)
    except Exception as e:
        await ctx.send(f'Co ty wyrabiasz panie??? ({e})')

@RollNinja.command()
async def r(ctx):
    """Patrz na !roll"""
    logc('r', ctx=ctx)
    await roll(ctx)

@RollNinja.command()
async def kronikarz(ctx):
    """Zapiski anonimowego obserwatora..."""
    logc('kronikarz', ctx=ctx)

    with open('data/kronika.txt', 'r') as file:
        sentences = file.readlines()
        selected_sentence = choice(sentences).strip()
    await ctx.send(selected_sentence)

@RollNinja.command()
async def days(ctx):
    """Opis emotek, które odpowiadają danym dniom tygodnia"""
    logc('days', ctx=ctx)

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
    
@RollNinja.command()
async def kiedysesja(ctx):
    """Podaje schedule sesji na ten tydzień"""
    logc('kiedysesja', ctx=ctx)
    channel = ctx.message.channel
    message_id = dbf.db_get_last_message(str(channel))
    try:
        message = await channel.fetch_message(message_id)
        if not message:
            raise Exception(f'Not message found // kiedysesja / {str(channel)}')
    except:
        await ctx.send('Nie wiadomo kiedy będzie najbliższa sesja')
        return
    
    new_message = ''
    for r in message.reactions:
        messages = [str(rr) async for rr in r.users() if rr != RollNinja.user]
        if messages:
            new_message += f'- {r} - {",".join(messages)} - ({len(messages)})\n'

    if new_message != '':
        await message.reply(new_message)    
    await message.reply('Nie wiadomo kiedy będzie najbliższa sesja, nikt się nie zapisał.')

@RollNinja.command()
async def gdziesesja(ctx):
    """Wywindowuje do ostatniego zapytania o sesje"""
    logc('gdziesesja', ctx=ctx)

    channel = ctx.message.channel
    message_id = dbf.db_get_last_message(str(channel))

    try:
        message = await channel.fetch_message(message_id)
        if not message:
            raise Exception(f'Not message found // kiedysesja / {str(channel)}')
    except:
        await ctx.send('Nie wiadomo gdzie będzie najbliższa sesja')
        return
    
    await message.reply('Prosze Wasza Wysokość.')