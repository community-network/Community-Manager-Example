import discord
import asyncio

async def setup(self, ctx):
    guildID = ctx.guild.id
    id = ctx.author.id
    if ctx.author.id == ctx.guild.owner.id or ctx.author.id == 140391046822494208:
        def check(m):
            return m.author.id == ctx.author.id
        await ctx.send("**You have 60 seconds to answer each question!**")
        await ctx.send(f"**Enter the name of the category you wish to create the channels in:(e.g Voice Channels)**")
        try:
            category = await self.bot.wait_for('message', check=check, timeout = 60.0)
        except asyncio.TimeoutError:
            await ctx.send('Took too long to answer!')
        else:
            new_cat = await ctx.guild.create_category_channel(category.content)
            await ctx.send('**Enter the name of the voice channel: (e.g Join To Create)**')
            try:
                channel = await self.bot.wait_for('message', check=check, timeout = 60.0)
            except asyncio.TimeoutError:
                await ctx.send('Took too long to answer!')
            else:
                try:
                    channel = await ctx.guild.create_voice_channel(channel.content, category=new_cat)
                    await self.bot.voiceGuild.upsert({"_id": guildID, "ownerID": id, "voiceChannelID": channel.id, "voiceCategoryID":new_cat.id}) # _id == guildID
                    await ctx.send("**You are all setup and ready to go!**")
                except:
                    await ctx.send("You didn't enter the names properly.\nUse `.voice setup` again!")
    else:
        await ctx.send(f"{ctx.author.mention} only the owner of the server can setup the bot!")

async def lock(self, ctx):
    id = ctx.author.id
    try:
        voice = await self.bot.voiceChannel.find(id)
        if voice is None:
            await ctx.send(f"{ctx.author.mention} You don't own a channel.")
        else:
            channelID = voice["voiceID"]
            role = discord.utils.get(ctx.guild.roles, name='@everyone')
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=False,read_messages=True)
            await ctx.send(f'{ctx.author.mention} Voice chat locked! 🔒')
    except:
        pass

async def unlock(self, ctx):
    id = ctx.author.id
    try:
        voice = await self.bot.voiceChannel.find(id)
        if voice is None:
            await ctx.send(f"{ctx.author.mention} You don't own a channel.")
        else:
            channelID = voice["voiceID"]
            role = discord.utils.get(ctx.guild.roles, name='@everyone')
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=True,read_messages=True)
            await ctx.send(f'{ctx.author.mention} Voice chat unlocked! 🔓')
    except:
        pass

async def permit(self, ctx, member : discord.Member):
    id = ctx.author.id
    try:
        voice = await self.bot.voiceChannel.find(id)
        if voice is None:
            await ctx.send(f"{ctx.author.mention} You don't own a channel.")
        else:
            channelID = voice["voiceID"]
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(member, connect=True)
            await ctx.send(f'{ctx.author.mention} You have permited {member.name} to have access to the channel. ✅')
    except:
        pass

async def reject(self, ctx, member : discord.Member):
    id = ctx.author.id
    guildID = ctx.guild.id
    try:
        voice = await self.bot.voiceChannel.find(id)
        if voice is None:
            await ctx.send(f"{ctx.author.mention} You don't own a channel.")
        else:
            channelID = voice["voiceID"]
            channel = self.bot.get_channel(channelID)
            for members in channel.members:
                if members.id == member.id:
                    voice = await self.bot.voiceGuild.find(guildID)
                    channel2 = self.bot.get_channel(voice["voiceChannelID"])
                    await member.move_to(channel2)
            await channel.set_permissions(member, connect=False,read_messages=True)
            await ctx.send(f'{ctx.author.mention} You have rejected {member.name} from accessing the channel. ❌')
    except:
        pass

async def channellimit(self, ctx, limit):
    id = ctx.author.id
    voice = await self.bot.voiceChannel.find(id)
    if voice is None:
        await ctx.send(f"{ctx.author.mention} You don't own a channel.")
    else:
        channelID = voice["voiceID"]
        channel = self.bot.get_channel(channelID)
        await channel.edit(user_limit = limit)
        await ctx.send(f'{ctx.author.mention} You have set the channel limit to be '+ '{}!'.format(limit))      
        setting = await self.bot.voiceUserSettings.find(id)
        if setting is None:
            bitrateLimit = ctx.guild.bitrate_limit
            await self.bot.voiceUserSettings.upsert({"_id": id, "channelName": f'{ctx.author.name}', "channelLimit": limit, "bitrateLimit": bitrateLimit}) # _id==userID
        else:
            await self.bot.voiceUserSettings.upsert({"_id": id, "channelName": setting["channelName"], "channelLimit": limit, "bitrateLimit": setting["bitrateLimit"]}) # _id==userID

async def channelname(self, ctx, name):
    id = ctx.author.id
    voice = await self.bot.voiceChannel.find(id)
    if voice is None:
        await ctx.send(f"{ctx.author.mention} You don't own a channel.")
    else:
        channelID = voice["voiceID"]
        channel = self.bot.get_channel(channelID)
        await channel.edit(name = name)
        await ctx.send(f'{ctx.author.mention} You have changed the channel name to '+ '{}!'.format(name))
        setting = await self.bot.voiceUserSettings.find(id)
        if setting is None:
            bitrateLimit = ctx.guild.bitrate_limit
            await self.bot.voiceUserSettings.upsert({"_id": id, "channelName": name, "channelLimit": 0, "bitrateLimit": bitrateLimit}) # _id==userID
        else:
            await self.bot.voiceUserSettings.upsert({"_id": id, "channelName": name, "channelLimit": setting["channelLimit"], "bitrateLimit": setting["bitrateLimit"]}) # _id==userID

async def bitratechannel(self, ctx, bitrate:int):
    id = ctx.author.id
    voice = await self.bot.voiceChannel.find(id)
    bitrateLimit = ctx.guild.bitrate_limit
    if int(bitrate*1000) > bitrateLimit:
        await ctx.send(f'{ctx.author.mention} {bitrate}kbps is higher than this discord server allows')
    elif int(bitrate) < 8:
        await ctx.send(f'{ctx.author.mention} {bitrate}kbps is lower than the lowest possible value')
    else:
        if voice is None:
            await ctx.send(f"{ctx.author.mention} You don't own a channel.")
        else:
            channelID = voice["voiceID"]
            channel = self.bot.get_channel(channelID)
            await channel.edit(bitrate = int(bitrate*1000))
            await ctx.send(f'{ctx.author.mention} You have changed the channel bitrate to '+ '{} kbps!'.format(bitrate))
            setting = await self.bot.voiceUserSettings.find(id)
            if setting is None:
                await self.bot.voiceUserSettings.upsert({"_id": id, "channelName": f'{ctx.author.name}', "channelLimit": 0, "bitrateLimit": int(bitrate*1000)}) # _id==userID
            else:
                await self.bot.voiceUserSettings.upsert({"_id": id, "channelName": setting["channelName"], "channelLimit": setting["channelLimit"], "bitrateLimit": int(bitrate*1000)}) # _id==userID

async def help(self, ctx):
    embed = discord.Embed(title="Voicecommands", description=f'**Lock your channel by using the following command:**\n`!voice lock`\n\n'
                    f'**Unlock your channel by using the following command:**\n`!voice unlock`\n\n'
                    f'**Change your channel name by using the following command:**\n`!voice name <name>`\n**Example:** `!voice name EU 5kd+`\n\n'
                    f'**Change your channel limit by using the following command:**\n`!voice limit number`\n**Example:** `!voice limit 2`\n\n'
                    f'**Give users permission to join by using the following command:**\n`!voice permit @person`\n**Example:** `!voice permit @iiTzArcur#0001`\n\n'
                    f'**Remove permission and the user from your channel using the following command:**\n`!voice reject @person`\n**Example:** `!voice reject @iiTzArcur#0001`\n\n',color=0x7289da)
    await ctx.send(embed=embed)
