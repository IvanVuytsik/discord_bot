from discord.ext.commands import when_mentioned_or, has_permissions, command
from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure


from ..db import db


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    #-----------------------------------prefix-----------------------------------------
    @command(name='prefix')
    @has_permissions(manage_guild=True)
    async def change_prefix(self, ctx, new: str):
        if len(new) > 5:
            await ctx.send('Prefix is limited to 5 characters')
        else:
            db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?", new, ctx.guild.id)
            await ctx.send(f"Prefix set to {new}")

    @change_prefix.error
    async def change_prefix_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Manage Server permission required!")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('misc')

def setup(bot):
    bot.add_cog(Misc(bot))