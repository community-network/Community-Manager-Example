import discord
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
from discord.utils import get

# this cog says a welcome message if someone joins and adds a role to the user.

# for setup:
# which guild it needs to check for new members: (guild ID - number)
GUILD = 0
# role to give out (role ID - number)
ROLE = 0
# also uncomment the cog from the main python file.

class BoB_Only(commands.Cog):
    """origin-api's Battlefield cog"""
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = self.bot.get_guild(GUILD)
        if member.guild.id == guild.id:
            channel = member.guild.system_channel
            if channel is not None:
                await channel.send('Welcome {0.mention}.'.format(member))
            role = get(member.guild.roles, id=ROLE)
            await member.add_roles(role)

def setup(bot):
    bot.add_cog(BoB_Only(bot))