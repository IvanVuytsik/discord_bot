from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown
from discord.ext.commands import CommandNotFound, BadArgument
from discord import Embed, Member
from random import choice, randint
from aiohttp import request
from typing import Optional


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='hello', aliases=['hi'], hidden=False)
    async def say_hello(self, ctx):
        await ctx.send(f'{choice(("Hello", "Hi", "Hey", "Greetings"))} {ctx.author.mention}!')

    @command(name='dice',  aliases=['roll'], hidden=False)
    @cooldown(1,60,BucketType.user) #times/seconds lasts/
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split('d'))
        if dice <=25:
            rolls = [randint(1,value) for i in range(dice)]
            await ctx.send(' + '.join([str(r) for r in rolls]) + f" = {sum(rolls)}")
        else:
            await ctx.send("I can\'t roll that many!")
    # @roll_dice.error
    # async def roll_dice_error(self, ctx, exc):
    #     if isinstance(exc.original, HTTPException):
    #         await ctx.send("Result value is too long. Please try a lower number")



    @command(name='slap', aliases=['hit'], hidden=False)
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "no reason"):
        await ctx.send(f'{ctx.author.display_name} slapped {member.mention} for {reason}!')

    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("This member is not found")



    @command(name='echo', aliases=['say'], hidden=False)
    @cooldown(1,20,BucketType.guild)
    async def echo_message(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    @command(name='fact')
    @cooldown(1,20,BucketType.guild)
    async def animal_fact(self, ctx, animal:str):
        if (animal :=animal.lower()) in ('dog', 'cat', 'fox', 'panda', 'raccoon', 'koala', 'bird'):
            fact_url =f"https://some-random-api.ml/facts/{animal}"
            image_url =f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"


            async with request ("GET", image_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    image_link = data['link']

                else:
                    image_link = None

            async with request ("GET", fact_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()

                    embed = Embed(title=f'{animal.title()} fact',
                                  description=data['fact'],
                                  color=ctx.author.colour)

                    if image_link is not None:
                        embed.set_image(url=image_link)


                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f'APT returned a {response.status} status')
        else:
            await ctx.send('No facts available')


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('fun') #file name

       # await self.bot.stdout.send('Fun is working')
        #print('fun cog ready')



def setup(bot):
    bot.add_cog(Fun(bot))
