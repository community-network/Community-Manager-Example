import discord
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
from discord.utils import get
import io

# this cog lets user suggest stuff anonymously with !suggest,
# after they made their suggestion the original message gets deleted and added to the suggest channel with the emoji's within Emojis[]

# for setup:
# the guild it needs to react for the !suggest message (guild ID - number)
guild = 0
# channel to put the suggestions into (channel ID - number)
suggestionChannel = 0
# emoji's to use for up and downvote
Emojis = ["⬆️","⬇️"]
# staffrole that menages the suggestions: !approve !deny !remove (role ID - number)
staff = 0
# also setup the mongoDB database if you havent already and uncomment the cog from the main python file.

class BoB_Only(commands.Cog):
    """origin-api's Battlefield cog"""
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    @commands.command(pass_context=True, name="suggestion", aliases=["suggest"], description="make a new suggestion")
    async def suggestion(self, ctx, *, suggestion):
        """**Example**: !suggest (type your suggestion here)"""
        if ctx.guild.id == guild:
            channel = self.bot.get_channel(suggestionChannel)
            list = await self.bot.suggestions.get_all()
            embed = discord.Embed(color=0xFFA500, title=f'Suggestion #{len(list)+1}:', description=suggestion)
            embed.set_author(name="Anonymous", icon_url="https://images-ext-1.discordapp.net/external/goXavQ0zzaSkv9RaOMTZEOa7Gs4a8LfOA8oGcE9XWmw/https/i.imgur.com/y43mMnP.png")
            message = await channel.send(embed=embed)
            await ctx.message.delete()
            await self.bot.suggestions.upsert({"_id": len(list)+1, "messageID": message.id, "channelID": message.channel.id, "suggestion": suggestion, "author": ctx.author.id})
            for Emoji in Emojis:
                await message.add_reaction(Emoji)
            
    @suggestion.error
    async def suggestion_error(self, ctx, error):
        embed = discord.Embed(color=0xe74c3c, description="Type the suggestion behind the command")
        await ctx.send(embed=embed)

    @commands.command(name="approve", aliases=["accept", "approved"], description="Approve the suggestion")
    @commands.guild_only()
    @commands.has_any_role(staff) # BoB-Staff role
    async def approve(self, ctx, messageNumber: int, message): # role.id
        """**Example**: !approve (number) (reason)"""
        data = await self.bot.suggestions.find(messageNumber)
        channel = self.bot.get_channel(data["channelID"])
        msg = await channel.fetch_message(data["messageID"])
        embed = discord.Embed(color=0x5BC236, title=f'Suggestion #{data["_id"]}: (Approved)', description=data["suggestion"])
        embed.set_author(name="Anonymous", icon_url="https://images-ext-1.discordapp.net/external/goXavQ0zzaSkv9RaOMTZEOa7Gs4a8LfOA8oGcE9XWmw/https/i.imgur.com/y43mMnP.png")
        embed.add_field(name=f"{ctx.message.author.name} approved the suggestion!", value=message)
        await msg.edit(embed=embed)
            
        # send message to author
        target = discord.utils.get(ctx.guild.members, id=data["author"])
        embed = discord.Embed(color=0x5BC236 , title=f'Your suggestion #{data["_id"]}, was approved by {ctx.message.author.name}. reason:', description=message)
        await target.send(embed=embed)

    @approve.error
    async def approve_error(self, ctx, error):
        embed = discord.Embed(color=0xe74c3c, description="!approve (valid suggestionnumber) (reason)")
        await ctx.send(embed=embed)

    @commands.command(name="deny", aliases=["denied"], description="Deny the suggestion")
    @commands.guild_only()
    @commands.has_any_role(staff) # BoB-Staff role
    async def deny(self, ctx, messageNumber: int, message): # role.id
        """**Example**: !deny (number) (reason)"""
        data = await self.bot.suggestions.find(messageNumber)
        channel = self.bot.get_channel(data["channelID"])
        msg = await channel.fetch_message(data["messageID"])
        embed = discord.Embed(color=0x990000 , title=f'Suggestion #{data["_id"]}: (Denied)', description=data["suggestion"])
        embed.set_author(name="Anonymous", icon_url="https://images-ext-1.discordapp.net/external/goXavQ0zzaSkv9RaOMTZEOa7Gs4a8LfOA8oGcE9XWmw/https/i.imgur.com/y43mMnP.png")
        embed.add_field(name=f"{ctx.message.author.name} denied the suggestion", value=message)
        await msg.edit(embed=embed)
            
        # send message to author
        target = discord.utils.get(ctx.guild.members, id=data["author"])
        embed = discord.Embed(color=0x990000 , title=f'Your suggestion #{data["_id"]}, was denied by {ctx.message.author.name}. reason:', description=message)
        await target.send(embed=embed)

    @deny.error
    async def deny_error(self, ctx, error):
        embed = discord.Embed(color=0xe74c3c, description="!deny (valid suggestionnumber) (reason)")
        await ctx.send(embed=embed)

    @commands.command(name="remove", aliases=["removed"], description="remove the suggestion")
    @commands.guild_only()
    @commands.has_any_role(staff) # BoB-Staff role
    async def remove(self, ctx, messageNumber: int, message): # role.id
        """**Example**: !remove (number) (reason)"""
        data = await self.bot.suggestions.find(messageNumber)
        channel = self.bot.get_channel(data["channelID"])
        msg = await channel.fetch_message(data["messageID"])
        await msg.delete()

        # send message to author
        target = discord.utils.get(ctx.guild.members, id=data["author"])
        embed = discord.Embed(color=0x990000 , title=f'Your suggestion #{data["_id"]}, was removed by {ctx.message.author.name}. reason:', description=message)
        await target.send(embed=embed)
            
    @remove.error
    async def remove_error(self, ctx, error):
        embed = discord.Embed(color=0xe74c3c, description="!remove (valid suggestionnumber) (reason)")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(BoB_Only(bot))