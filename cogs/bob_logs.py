import discord
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
import datetime

# this cog posts messages if a user got banned in the logs channel

# for setup:
# channel to post bans to (channel ID - number)
logChannel = 0
# also uncomment the cog from the main python file.

def predicate(event):
    return event.action is discord.AuditLogAction.ban

class BoB_Logs(commands.Cog):
    """origin-api's Battlefield cog"""
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user: discord.User):
        event = await guild.audit_logs().find(predicate)
        embed = discord.Embed(title=f"Member Banning Case", colour=discord.Colour.red())
        embed.add_field(name="Member Name", value=user.name)
        embed.add_field(name="Reason", value=event.reason)
        embed.add_field(name="By user", value=event.user)
        embed.set_footer(text=f"User ID: {user.id}")
        embed.timestamp = datetime.datetime.utcnow()
        channel = self.bot.get_channel(id=logChannel)
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BoB_Logs(bot))