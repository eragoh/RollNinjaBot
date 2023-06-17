import discord
from discord.ext import commands, tasks
import datetime
import asyncio
from random import randint, choice

from json_data import data, emojis, quotes

class RollNinjaBot(commands.Bot):
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)

    def fight(self, token):
        self.run(token)

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def setup_hook(self):
        channel_name = 'artefakt-rpg'
        #channel_name = 'poligon'
        self.reminder.start(channel_name)
        self.remind_late_players.start(channel_name)

    async def on_message(self, message):
        if message.content.startswith('!'):
            await self.process_commands(message)
            return
        if message.author == self.user:
            return
        
        #print(message)
        #print(message.content)
    
    @tasks.loop(seconds=data["reminder_time"])
    async def reminder(self, channel_name):
        channel = self.get_channel(data["channels"][channel_name]["id"])
        message = await channel.send(f'# Drodzy gracze! Kiedy możecie w tym tygodniu grać w <@&{data["channels"][channel_name]["role"]}>?')
        for em in ["Mon", "Tu", "Wed", "Th", "Fr", "Sat", "Sun", "x"]:
            await message.add_reaction(emojis[em])
        self.save_message_id_reminder(message.id)
        
            #await channel.send(" ".join(member.mention for member in channel.members if not member.bot))

    @reminder.before_loop
    async def before_reminder(self):
        target_time = datetime.time(9, 0)
        current_day = datetime.datetime.now().date().weekday()
        days_until_sunday = (6 - current_day) % 7
        next_sunday = datetime.datetime.now() + datetime.timedelta(days=days_until_sunday)
        next_sunday = next_sunday.replace(hour=target_time.hour, minute=target_time.minute)
        remaining_time = int((next_sunday - datetime.datetime.now()).total_seconds())
        remaining_time = 1
        await asyncio.sleep(remaining_time)
        await self.wait_until_ready()

    @tasks.loop(seconds=data["reminder_to_reminder_time"])
    async def remind_late_players(self, channel_name):
        channel = self.get_channel(data["channels"][channel_name]["id"])
        message_id = self.check_last_reminder()
        if message_id:
            message = await channel.fetch_message(int(message_id))
            guild = self.get_guild(data["guild"])
            role = discord.utils.get(guild.roles, id=data["channels"][channel_name]["role"])
            l = set()
            for r in message.reactions:
                async for rr in r.users():
                    l.add(rr)
            members = []
            for member in channel.members:
                if role in member.roles:
                    if not member in l:
                        members.append(member)
            if members:
                remind_users = ' '.join(f'{member.mention}' for member in members)
                await message.reply(choice(quotes["reminders"]).replace('[user]', f'{remind_users}'))

    @remind_late_players.before_loop
    async def before_remind_late_players(self):
        t = datetime.datetime.now()
        remaining_time = (59  - t.minute) * 60 + 60 - t.second
        remaining_time = 5
        await asyncio.sleep(remaining_time)
        await self.wait_until_ready()

    def check_last_reminder(self):
        with open('tmp/last_message_reminder', 'r') as f:
            message_id = f.read()
        return message_id
    def save_message_id_reminder(self, id):
        with open('tmp/last_message_reminder', 'w') as f:
            f.write(str(id))

RollNinja = RollNinjaBot()
       
@RollNinja.command()
async def xd(ctx):
    """Sam zobacz xD"""

    await ctx.send(quotes["xd"][randint(0, len(quotes["xd"]) -1)])

@RollNinja.command()
async def roll(ctx):
    """Rzut kośćmi w formacie mkn, np. 10k100"""

    try:
        message = ctx.message.content.split(' ')[1]
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

    await roll(ctx)

@RollNinja.command()
async def kronikarz(ctx):
    """Zapiski anonimowego obserwatora..."""

    with open('data/kronika.txt', 'r') as file:
        sentences = file.readlines()
        selected_sentence = choice(sentences).strip()
    await ctx.send(selected_sentence)

@RollNinja.command()
async def days(ctx):
    """Opis emotek, które odpowiadają danym dniom tygodnia"""

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

    message_id = RollNinja.check_last_reminder()
    channel = RollNinja.get_channel(data["channels"]["artefakt-rpg"]["id"])
    message = await channel.fetch_message(int(message_id))
    if message:
        days = {}
        for r in message.reactions:
            user_than_can_play = ''
            user_than_can_play_count = 0

            async for rr in r.users():
                if rr != RollNinja.user:
                    user_than_can_play += f'{rr}, '
                    user_than_can_play_count += 1
            days[r] = (user_than_can_play, user_than_can_play_count)

        new_message = ''

        for key in days:
            if days[key][1] != 0:
                new_message += f'- {key} - {days[key][0]} ({days[key][1]})\n'
        await message.reply(new_message)

    else:
        await ctx.send('Nie wiadomo kiedy będzie najbliższa sesja')
