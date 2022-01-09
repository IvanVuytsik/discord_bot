from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown
from discord.errors import HTTPException, Forbidden
from apscheduler.triggers.cron import CronTrigger
from glob import glob
from discord import Embed, File
from discord import Intents
from discord.ext.commands import Context
from datetime import datetime
from asyncio import sleep
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import when_mentioned_or, has_permissions, command
from ..db import db

OWNER_IDS = [883286041136627752]    # discord registered id
COGS = [path.split('\\')[-1][:-3] for path in glob('./library/cogs/*.py')]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument, MissingRequiredArgument)

def get_prefix(bot, message):
    prefix = db.field('SELECT prefix FROM guilds WHERE GuildID = ?', message.guild.id)
    return when_mentioned_or(prefix)(bot, message)


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f'{cog} cog ready')

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler(timezone='Europe/Amsterdam')

        #intents = Intents.default()
        #intents.members = True
        db.autosave(self.scheduler)
        super().__init__(command_prefix=get_prefix,
                         owner_ids=OWNER_IDS,
                         intents=Intents.all(),)

    def setup(self):
        for cog in COGS:
            self.load_extension(f"library.cogs.{cog}")
            print(f'{cog} cog loaded')
        print('setup complete')

    def run(self, version):
        self.VERSION = version

        print('running setup...')
        self.setup()

        with open('./library/bot/token.0', 'r', encoding='utf-8') as tf:
            self.TOKEN = tf.read()
        print('Running bot')
        super().run(self.TOKEN, reconnect=True)


    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)
        if ctx.command != None and ctx.guild != None:
            if self.ready:
                await self.invoke(ctx)
            else:
                await ctx.send("Not ready for a new command!")

    async def rules_reminder(self):
        await self.stdout.send('Timed notification')

#----------------------------------------------------------------------------------
    async def on_connect(self):
        print('bot connected')

    async def on_disconnect(self):
        print('bot disconnected')
#---------------------------------------------------------
    async def on_error(self, err, *args, **kwargs):
        if err == 'on_command_error':
            await args[0].send('Something went wrong')

        await self.stdout.send('An error occurred')
        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("One or more required arguments are missing")

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f"Is on {str(exc.cooldown.type).split('.')[-1]} cooldown. Try in {exc.retry_after:,.2f} seconds")

        elif hasattr(exc, 'original'):
        # elif isinstance(exc.original, HTTPException):
        #     await ctx.send("Unable to send message")
            if isinstance(exc, Forbidden):
                await ctx.send("No permission to do that")
            else:
                raise exc.original
        else:
            raise exc
#---------------------------------------------------------
    async def on_ready(self):
        if not self.ready:

            self.guild = self.get_guild(923777664509157446)
            self.stdout = self.get_channel(923777664509157449)
            self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0)) #second = '*/30' - every 30 sec
            self.scheduler.start()




            # embed = Embed(title="Now online!", description='Hi Bro! I am here',
            #               colour=0xFF0000, timestamp=datetime.utcnow())
            # fields = [('Name', 'Value', True),
            #           ('Another field', 'Another field', True),
            #           ('Non-inline field', 'Appears on its own row', False)]
            # for name, value, inline in fields:
            #     embed.add_field(name=name,value=value, inline=inline)
            # embed.set_author(name="vanya's bot",icon_url=self.guild.icon_url) #author
            # embed.set_footer(text="Footer") #footer
            # embed.set_thumbnail(url=self.guild.icon_url)    #add img
            # embed.set_image(url=self.guild.icon_url)    #add img
            # await channel.send(embed=embed)
            #
            # await channel.send(file=File('./img/profile.png'))  #sending files
            #embed.add_field(name='Name', value='Value', inline=True)

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            await self.stdout.send('Now online')
            self.ready = True
            print('bot ready')
        else:
            print("bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()