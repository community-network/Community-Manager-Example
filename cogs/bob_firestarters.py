import discord
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
import asyncio
from discord.utils import get

# lets people react to a message to give them a role, click again to remove.
# in bob its ment so admins can ping that role to notify people to start the servers

# for setup:
# message people can react to (message ID - number)
messageNumber = 0
# the role the bot gives to mark people as "firestarter" (channel ID - number)
fireStarterRole = 0
# guild where the role is in (guild ID - number)
fireStarterGuild = 0
# name of the message people can react to
createTitle = ":fire: Apply for @Firestarters role :fire:"
# description
createMessage = """**want to help us start our servers?**
                Click the emoji attached to this message to get notified when we're going to start the servers. It will give you the Firestarter role, we will ping that role every time we start our servers. You will receive VIP access to one of the servers of your choice as a thank you for helping us launch our servers.

                **how does seeding work:**
                We need 20 people (for a 64 player conquest server) in a server before you can actually play in the server, by joining the server with the rest of the people here the server will get to that magic number and start the game.

                *to remove the role: click on the emoji to remove your reaction*"""
# author of the message
createAuthorName = "Band of Brothers Firestarters"                    
# avatar of the author
createAuthorImage = "https://cdn.discordapp.com/icons/513749917567811586/a_4e2b54eb621216f63668e1715c7d5e17.png?size=128"
# color on the leftside of the embed
createAuthorColor = 0xFF9900
# the emoji people can react to
Emojis = ["🔥"]
# also uncomment the cog from the main python file.

class BoB_Firestarters(commands.Cog):
    """origin-api's Battlefield cog"""
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    # creates the firestarter message
    @commands.command(pass_context=True, name="createfirestarterssystembob", hidden=True)
    @commands.is_owner()
    async def createFirestarterEmbed(self, ctx):
        """creates a embed"""
        embed = discord.Embed(color=createAuthorColor, title=createTitle, description=createMessage)
        embed.set_author(name=createAuthorName, icon_url=createAuthorImage)
        createdMessage = await ctx.send(embed=embed)
        for Emoji in Emojis:
            await createdMessage.add_reaction(Emoji)

    @createFirestarterEmbed.error
    async def createFirestarterEmbed_error(self, ctx, error):
        embed = discord.Embed(color=0xe74c3c, description=error)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if reaction.message_id == messageNumber:
            role = get(reaction.member.guild.roles, id=fireStarterRole)
            await reaction.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction):
        if reaction.message_id == messageNumber:
            guild = self.bot.get_guild(fireStarterGuild)
            role = get(guild.roles, id=fireStarterRole)
            for member in guild.members:
                if member.id == reaction.user_id:
                    await member.remove_roles(role)
                    break

def setup(bot):
    bot.add_cog(BoB_Firestarters(bot))