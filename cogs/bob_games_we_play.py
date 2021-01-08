import discord
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
import asyncio
from discord.utils import get

# same concept as firestarters:
# lets people react to a message to give them a role, click again to remove.
# this is so people can show which games they play.

# admins can add games:
# !addgamerole :BF1~1: @Battlefield 1 Battlefield 1
# remove games:
# !removegamerole :BF1~1:

# for setup:
# message people can react to (message ID - number)
messageNumber = 0
# channel the message is in (channel ID - number)
messageChannel = 0
# guild to give the rank in (guild ID - number)
gamesGuild = 0
# embed title
createTitle = "Games We Play"
# embed description
createMessage = "Click on the emoji below of the game you play a lot to show it as a role, click again to remove"
# embed color on the left side
createColor = 0xFF9900
# the role with the people in it that can add games, DONT add people you dont trust with adding roles to people. best option is to only allow yourself to change it. (role ID - number)
ADMINROLE = 0
# also setup the mongoDB database if you havent already and uncomment the cog from the main python file.

async def updateMessage(self):
    channel = self.bot.get_channel(messageChannel)
    msg = await channel.fetch_message(messageNumber)
    embed = discord.Embed(color=createColor, title=createTitle)
    embed.set_footer(text=createMessage)
    list = await self.bot.config.get_all()
    for item in list:
        embed.add_field(name="\u200b", value=f'{item["_id"]} {item["gameName"]}', inline=True)
    await msg.edit(embed=embed)
    return msg

class BoB_GamesWePlay(commands.Cog):
    """origin-api's Battlefield cog"""
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    # create the message
    @commands.command(pass_context=True, name="creategamesweplaysystembob", hidden=True)
    @commands.is_owner()
    async def createFirestarterEmbed(self, ctx):
        """creates a embed"""
        embed = discord.Embed(color=createColor, title=createTitle)
        embed.set_footer(text=createMessage)
        await ctx.send(embed=embed)

    @createFirestarterEmbed.error
    async def createFirestarterEmbed_error(self, ctx, error):
        embed = discord.Embed(color=0xe74c3c, description=error)
        await ctx.send(embed=embed)


    # react to reaction add
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if reaction.message_id == messageNumber:
            data = await self.bot.config.find(str(reaction.emoji))
            # Make sure we have a useable role
            if not data or "role" not in data:
                return
            role = get(reaction.member.guild.roles, id=data["role"])
            await reaction.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction):
        if reaction.message_id == messageNumber:
            guild = self.bot.get_guild(gamesGuild)
            data = await self.bot.config.find(str(reaction.emoji))
            # Make sure we have a useable role
            if not data or "role" not in data:
                return
            role = get(guild.roles, id=data["role"])
            for member in guild.members:
                if member.id == reaction.user_id:
                    await member.remove_roles(role)
                    break

    # change game list
    @commands.command(name="addgamerole", description="add game to the GamesWePlay section")
    @commands.guild_only()
    @commands.has_any_role(ADMINROLE)
    async def addgamerole(self, ctx, emoji, role: discord.Role, *, gameName): 
        """**Example**: !addgamerole (:emoji:) (roleId) (gameName)"""
        await self.bot.config.upsert({"_id": emoji, "role": role.id, "gameName": gameName})
        msg = await updateMessage(self)
        await msg.add_reaction(emoji)

    @addgamerole.error
    async def addgamerole_error(self, ctx, error):
        embed = discord.Embed(color=0xe74c3c, description=error)
        await ctx.send(embed=embed)

    @commands.command(name="removegamerole", description="remove game from the GamesWePlay section")
    @commands.guild_only()
    @commands.has_any_role(ADMINROLE)
    async def removegamerole(self, ctx, emoji): 
        """**Example**: !removegamerole (:emoji:)"""
        await self.bot.config.delete(emoji)
        await updateMessage(self)

    @removegamerole.error
    async def removegamerole_error(self, ctx, error):
        embed = discord.Embed(color=0xe74c3c, description=error)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(BoB_GamesWePlay(bot))