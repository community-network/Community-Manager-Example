import discord
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
import asyncio
import io

# this cog lets users react on a message with a number.
# After a user pressed the emoji, the user can than type into that channel for 60 seconds.
# every message he sends there are instandly removed and put into the reports channel with the ping attached to the emoji.

# for setup:
# message it needs to check if a emoji is pressed (message ID - number)
messageNumber = 0
# channel where the ebove message is (channel ID - number)
infoChannelNumber = 0
# channel where it needs to post the reports (channel ID - number)
reportsChannelNumber = 0
# message with the emoji's title
createTitle = "How to report a player"
# description
createMessage = """Click on corresponding Server emoji to report a player.
                then, you will get access to write in this chat:

                the **origin name** and **Reason** why you report him

                Your message will be deleted, admins on server you choose will be notified.
                We delete your message so that cheaters cant read that you reported him.
                You'll have 60 seconds to type your message, otherwise you have to re-click the emoji."""
# emojilist with the role it pings if a message is posted after clicking the emoji ("emoji": role ID (number))
rolesToEmoji = {"1️⃣": 0, "2️⃣": 0, "3️⃣": 0, "4️⃣": 0, "5️⃣": 0}
# also uncomment the cog from the main python file.

# dont change this, internal
members = []

async def allowWriteInChannel(self, reaction):
    channel = self.bot.get_channel(infoChannelNumber)
    poll_message = await channel.fetch_message(messageNumber)
    global members
    members.append({"id": reaction.member.id, "emoji": reaction.emoji.name})
    await channel.set_permissions(reaction.member, read_messages=True, send_messages=True)

    await asyncio.sleep(60)
    await channel.set_permissions(reaction.member, overwrite=None)
    await asyncio.sleep(3)
    members.remove({"id": reaction.member.id, "emoji": reaction.emoji.name})
    await poll_message.remove_reaction(reaction.emoji, reaction.member)

class Report_System_Bob(commands.Cog):
    """origin-api's Battlefield cog"""
    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    # created the message where people can react with emojis to
    @commands.command(pass_context=True, name="createreportsystembob", hidden=True)
    @commands.is_owner()
    async def createBobReportEmbed(self, ctx):
        """creates a embed"""
        embed = discord.Embed(color=0xe74c3c, title=createTitle, description=createMessage)
        createdMessage = await ctx.send(embed=embed)
        for key in rolesToEmoji:
            await createdMessage.add_reaction(key)

    @createBobReportEmbed.error
    async def createBobReportEmbed_error(self, ctx, error):
        embed = discord.Embed(color=0xe74c3c, description=error)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if reaction.message_id == messageNumber:
            asyncio.ensure_future(allowWriteInChannel(self, reaction))

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction):
        try:
            if reaction.message_id == messageNumber:
                global members
                members.remove({"id": reaction.user_id, "emoji": reaction.emoji.name})
                channel = self.bot.get_channel(infoChannelNumber)
                user = self.bot.get_user(reaction.user_id)
                await channel.set_permissions(user, overwrite=None)
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            # check if in report channel, isnt the bot itself and has pressed a emoji
            if message.channel.id == infoChannelNumber and message.author.id != 755435360745553940:
                global members
                for member in members:
                    if message.author.id == member["id"]:
                        channel = self.bot.get_channel(reportsChannelNumber)
                        roleId = rolesToEmoji[member["emoji"]]
                        await channel.send(f"<@&{roleId}>")
                        embed = discord.Embed(color=0xFFA500, title=f'New report for {member["emoji"]}', description=message.content)
                        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
                        embed.add_field(name='joined:', value=message.author.joined_at)

                        if len(message.attachments) != 0:
                            fp = io.BytesIO()
                            await message.attachments[0].save(fp)
                            file = discord.File(fp, filename="image.png", spoiler=message.attachments[0].is_spoiler())
                            embed.set_image(url="attachment://image.png")
                            await channel.send(embed=embed, file=file)
                            # dm author with file
                            await message.author.send("The admins received your message,\nimages you send will come trough to the admins but not in dms")
                            await message.author.send(embed=embed, file=file)
                        else:
                            await channel.send(embed=embed)
                            # dm author without file
                            await message.author.send("The admins received your message,\nimages you send will come trough to the admins but not in dms")
                            await message.author.send(embed=embed)
                        await message.delete()
        except Exception as e:
            print(e)
        
async def setup(bot):
    await bot.add_cog(Report_System_Bob(bot))