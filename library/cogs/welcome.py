from discord.ext.commands import when_mentioned_or, has_permissions, command
from discord.ext.commands import Cog
from discord.errors import Forbidden

from ..db import db

class Welcome(Cog):
    def __init__(self, bot):
        self.bot = bot


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('welcome')


    @Cog.listener()
    async def on_member_join(self, member):
      db.execute('INSERT INTO exp (UserID) VALUES (?)', member.id)
      await self.bot.get_channel(925180842815389717).send(f"Welcome to *{member.guild.name}* {member.mention}! Head over to <#923777664509157449>")
      try:
          await member.send(f"Welcome *{member.guild.name}* Enjoy your stay!")
      except Forbidden:
          pass

      await member.add_roles(*(member.guild.get_role(id_) for id_ in (925168589076582410, 925168431240724511, 925167578110898257)))

      #await member.edit(roles=[member.guild.get_role(id_) for id_ in (925168589076582410, 925168431240724511, 925167578110898257)])

    @Cog.listener()
    async def on_member_remove(self, member):
        db.execute('DELETE FROM exp WHERE UserID=?', member.id)
        await self.bot.get_channel(925181091269210162).send(f"{member.display_name} has left {member.guild.name}")


def setup(bot):
    bot.add_cog(Welcome(bot))