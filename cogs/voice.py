import discord
import asyncio
from discord.ext import commands
from discord import app_commands
from .commands.voice import *

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
            if before.channel is not None:
                voiceChannel = await self.bot.voiceChannel.find_one({"voiceID": before.channel.id})
                if voiceChannel is not None:
                    if len(before.channel.members) == 0:
                        await before.channel.delete()
                        await asyncio.sleep(3)
                        await self.bot.voiceChannel.delete(voiceChannel["_id"])
                        
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

    @commands.hybrid_group(name="voice")
    async def voice(self, ctx):
        """`!voice help` for a list of voice related commands"""
        pass
    
    @voice.command(name="setup", description="setup the voice functions to this discord")
    async def voice_setup(self, ctx):
        await setup(self, ctx)

    @voice_setup.error
    async def info_error(self, ctx, error):
        print(error)

    @voice.command(name="lock", description="Lock your channel")
    async def voice_lock(self, ctx):
        await lock(self, ctx)

    @voice.command(name="unlock", description="Unlock your channel")
    async def voice_unlock(self, ctx):
        await unlock(self, ctx)

    @voice.command(name="permit", aliases=["allow"], description="Give users permission to join your channel")
    @app_commands.describe(member="Member to add")
    async def voice_permit(self, ctx, member : discord.Member):
        await permit(self, ctx, member)

    @voice.command(name="reject", aliases=["deny"], description="Remove permission to join your channel and remove")
    @app_commands.describe(member="Member to block")
    async def voice_reject(self, ctx, member : discord.Member):
        await reject(self, ctx, member)

    @voice.command(name="limit", description="Change your channel limit")
    @app_commands.describe(limit="Max amount of users")
    async def voice_limit(self, ctx, limit):
        await channellimit(self, ctx, limit)
                
    @voice.command(name="name", description="Change your channel name")
    @app_commands.describe(name="The new name of the channel")
    async def voice_name(self, ctx,*, name):
        await channelname(self, ctx, name)

    @voice.command(name="bitrate", description="Change your channel bitrate")
    @app_commands.describe(bitrate="Bitrate")
    async def voice_bitrate(self, ctx, bitrate:int):
        await bitratechannel(self, ctx, bitrate)

    @voice.command(name="help", description="The list of commands for the voice functionality")
    async def voice_help(self, ctx):
        await help(self, ctx)
        
async def setup(bot):
    await bot.add_cog(voice(bot))




