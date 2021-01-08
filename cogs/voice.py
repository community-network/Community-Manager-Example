import discord
import asyncio
from discord.ext import commands

# this cogs lets users create temporary voice channels,
# the user has to join a "join to create" channel, he will get instandly moved to a channel called:
# user's channel, the channel will be automaticly removed after everyone has left the channel created.

# no setup required within this file, just setup the mongoDB database and uncumment the line for the cog to use this. 
# setup command: !voice setup

class voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guildID = member.guild.id
        try:
            voice = await self.bot.voiceGuild.find(guildID)
        except:
            voice = None
        if voice is None:
            pass
        else:
            voiceID = voice["voiceChannelID"]
            if after.channel is None:
                pass
            else:
                if after.channel.id == voiceID:
                    setting = await self.bot.voiceUserSettings.find(member.id)
                    guildSetting = await self.bot.voiceGuildSettings.find(guildID)
                    bitrateLimit = member.guild.bitrate_limit
                    if setting is None:
                        name = f"{member.name}'s channel"
                        if guildSetting is None:
                            limit = 0
                        else:
                            limit = guildSetting["channelLimit"]
                    else:
                        if guildSetting is None:
                            name = setting["channelName"]
                            limit = setting["channelLimit"]
                        elif guildSetting is not None and setting["channelLimit"] == 0:
                            name = setting["channelName"]
                            limit = guildSetting["channelLimit"]
                        else:
                            name = setting["channelName"]
                            limit = setting["channelLimit"]
                            bitrateLimit = setting["bitrateLimit"]
                    categoryID = voice["voiceCategoryID"]
                    id = member.id
                    category = self.bot.get_channel(categoryID)
                    channel2 = await member.guild.create_voice_channel(name,category=category,bitrate=bitrateLimit)
                    channelID = channel2.id
                    await member.move_to(channel2)
                    await channel2.set_permissions(self.bot.user, connect=True,read_messages=True)
                    await channel2.edit(name= name, user_limit = limit)
                    await self.bot.voiceChannel.upsert({"_id": id, "voiceID": channelID}) # _id==userID
                    def check(a,b,c):
                        return len(channel2.members) == 0
                    await self.bot.wait_for('voice_state_update', check=check)
                    await channel2.delete()
                    await asyncio.sleep(3)
                    await self.bot.voiceChannel.delete(id) # _id==userID

    @commands.group()
    async def voice(self, ctx):
        """`!voice help` for a list of voice related commands"""
        pass
    
    @voice.command()
    async def setup(self, ctx):
        guildID = ctx.guild.id
        id = ctx.author.id
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id == 140391046822494208:
            def check(m):
                return m.author.id == ctx.author.id
            await ctx.channel.send("**You have 60 seconds to answer each question!**")
            await ctx.channel.send(f"**Enter the name of the category you wish to create the channels in:(e.g Voice Channels)**")
            try:
                category = await self.bot.wait_for('message', check=check, timeout = 60.0)
            except asyncio.TimeoutError:
                await ctx.channel.send('Took too long to answer!')
            else:
                new_cat = await ctx.guild.create_category_channel(category.content)
                await ctx.channel.send('**Enter the name of the voice channel: (e.g Join To Create)**')
                try:
                    channel = await self.bot.wait_for('message', check=check, timeout = 60.0)
                except asyncio.TimeoutError:
                    await ctx.channel.send('Took too long to answer!')
                else:
                    try:
                        channel = await ctx.guild.create_voice_channel(channel.content, category=new_cat)
                        await self.bot.voiceGuild.upsert({"_id": guildID, "ownerID": id, "voiceChannelID": channel.id, "voiceCategoryID":new_cat.id}) # _id == guildID
                        await ctx.channel.send("**You are all setup and ready to go!**")
                    except:
                        await ctx.channel.send("You didn't enter the names properly.\nUse `.voice setup` again!")
        else:
            await ctx.channel.send(f"{ctx.author.mention} only the owner of the server can setup the bot!")

    @setup.error
    async def info_error(self, ctx, error):
        print(error)

    @voice.command()
    async def lock(self, ctx):
        id = ctx.author.id
        try:
            voice = await self.bot.voiceChannel.find(id)
            if voice is None:
                await ctx.channel.send(f"{ctx.author.mention} You don't own a channel.")
            else:
                channelID = voice["voiceID"]
                role = discord.utils.get(ctx.guild.roles, name='@everyone')
                channel = self.bot.get_channel(channelID)
                await channel.set_permissions(role, connect=False,read_messages=True)
                await ctx.channel.send(f'{ctx.author.mention} Voice chat locked! 🔒')
        except:
            pass

    @voice.command()
    async def unlock(self, ctx):
        id = ctx.author.id
        try:
            voice = await self.bot.voiceChannel.find(id)
            if voice is None:
                await ctx.channel.send(f"{ctx.author.mention} You don't own a channel.")
            else:
                channelID = voice["voiceID"]
                role = discord.utils.get(ctx.guild.roles, name='@everyone')
                channel = self.bot.get_channel(channelID)
                await channel.set_permissions(role, connect=True,read_messages=True)
                await ctx.channel.send(f'{ctx.author.mention} Voice chat unlocked! 🔓')
        except:
            pass

    @voice.command(aliases=["allow"])
    async def permit(self, ctx, member : discord.Member):
        id = ctx.author.id
        try:
            voice = await self.bot.voiceChannel.find(id)
            if voice is None:
                await ctx.channel.send(f"{ctx.author.mention} You don't own a channel.")
            else:
                channelID = voice["voiceID"]
                channel = self.bot.get_channel(channelID)
                await channel.set_permissions(member, connect=True)
                await ctx.channel.send(f'{ctx.author.mention} You have permited {member.name} to have access to the channel. ✅')
        except:
            pass

    @voice.command(aliases=["deny"])
    async def reject(self, ctx, member : discord.Member):
        id = ctx.author.id
        guildID = ctx.guild.id
        try:
            voice = await self.bot.voiceChannel.find(id)
            if voice is None:
                await ctx.channel.send(f"{ctx.author.mention} You don't own a channel.")
            else:
                channelID = voice["voiceID"]
                channel = self.bot.get_channel(channelID)
                for members in channel.members:
                    if members.id == member.id:
                        voice = await self.bot.voiceGuild.find(guildID)
                        channel2 = self.bot.get_channel(voice["voiceChannelID"])
                        await member.move_to(channel2)
                await channel.set_permissions(member, connect=False,read_messages=True)
                await ctx.channel.send(f'{ctx.author.mention} You have rejected {member.name} from accessing the channel. ❌')
        except:
            pass

    @voice.command()
    async def limit(self, ctx, limit):
        id = ctx.author.id
        voice = await self.bot.voiceChannel.find(id)
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} You don't own a channel.")
        else:
            channelID = voice["voiceID"]
            channel = self.bot.get_channel(channelID)
            await channel.edit(user_limit = limit)
            await ctx.channel.send(f'{ctx.author.mention} You have set the channel limit to be '+ '{}!'.format(limit))      
            setting = await self.bot.voiceUserSettings.find(id)
            if setting is None:
                bitrateLimit = ctx.guild.bitrate_limit
                await self.bot.voiceUserSettings.upsert({"_id": id, "channelName": f'{ctx.author.name}', "channelLimit": limit, "bitrateLimit": bitrateLimit}) # _id==userID
            else:
                await self.bot.voiceUserSettings.upsert({"_id": id, "channelName": setting["channelName"], "channelLimit": limit, "bitrateLimit": setting["bitrateLimit"]}) # _id==userID
                
    @voice.command()
    async def name(self, ctx,*, name):
        id = ctx.author.id
        voice = await self.bot.voiceChannel.find(id)
        if voice is None:
            await ctx.channel.send(f"{ctx.author.mention} You don't own a channel.")
        else:
            channelID = voice["voiceID"]
            channel = self.bot.get_channel(channelID)
            await channel.edit(name = name)
            await ctx.channel.send(f'{ctx.author.mention} You have changed the channel name to '+ '{}!'.format(name))
            setting = await self.bot.voiceUserSettings.find(id)
            if setting is None:
                bitrateLimit = ctx.guild.bitrate_limit
                await self.bot.voiceUserSettings.upsert({"_id": id, "channelName": name, "channelLimit": 0, "bitrateLimit": bitrateLimit}) # _id==userID
            else:
                await self.bot.voiceUserSettings.upsert({"_id": id, "channelName": name, "channelLimit": setting["channelLimit"], "bitrateLimit": setting["bitrateLimit"]}) # _id==userID
 
    @voice.command()
    async def bitrate(self, ctx,*, bitrate:int):
        id = ctx.author.id
        voice = await self.bot.voiceChannel.find(id)
        bitrateLimit = ctx.guild.bitrate_limit
        if int(bitrate*1000) > bitrateLimit:
            await ctx.channel.send(f'{ctx.author.mention} {bitrate}kbps is higher than this discord server allows')
        elif int(bitrate) < 8:
            await ctx.channel.send(f'{ctx.author.mention} {bitrate}kbps is lower than the lowest possible value')
        else:
            if voice is None:
                await ctx.channel.send(f"{ctx.author.mention} You don't own a channel.")
            else:
                channelID = voice["voiceID"]
                channel = self.bot.get_channel(channelID)
                await channel.edit(bitrate = int(bitrate*1000))
                await ctx.channel.send(f'{ctx.author.mention} You have changed the channel bitrate to '+ '{} kbps!'.format(bitrate))
                setting = await self.bot.voiceUserSettings.find(id)
                if setting is None:
                    await self.bot.voiceUserSettings.upsert({"_id": id, "channelName": f'{ctx.author.name}', "channelLimit": 0, "bitrateLimit": int(bitrate*1000)}) # _id==userID
                else:
                    await self.bot.voiceUserSettings.upsert({"_id": id, "channelName": setting["channelName"], "channelLimit": setting["channelLimit"], "bitrateLimit": int(bitrate*1000)}) # _id==userID

    @voice.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Voicecommands", description=f'**Lock your channel by using the following command:**\n`.voice lock`\n\n'
                        f'**Unlock your channel by using the following command:**\n`!voice unlock`\n\n'
                        f'**Change your channel name by using the following command:**\n`!voice name <name>`\n**Example:** `.voice name EU 5kd+`\n\n'
                        f'**Change your channel limit by using the following command:**\n`!voice limit number`\n**Example:** `.voice limit 2`\n\n'
                        f'**Give users permission to join by using the following command:**\n`!voice permit @person`\n**Example:** `.voice permit @iiTzArcur#0001`\n\n'
                        f'**Remove permission and the user from your channel using the following command:**\n`!voice reject @person`\n**Example:** `.voice reject @iiTzArcur#0001`\n\n',color=0x7289da)
        await ctx.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(voice(bot))




