import discord
import asyncio
from discord.abc import User
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
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

    @commands.group()
    async def voice(self, ctx):
        """`!voice help` for a list of voice related commands"""
        pass
    
    @voice.command(name="setup")
    async def voice_setup(self, ctx):
        await setup(self, ctx)

    @voice_setup.error
    async def info_error(self, ctx, error):
        print(error)

    @voice.command(name="lock")
    async def voice_lock(self, ctx):
        await lock(self, ctx)

    @voice.command(name="unlock")
    async def voice_unlock(self, ctx):
        await unlock(self, ctx)

    @voice.command(name="permit", aliases=["allow"])
    async def voice_permit(self, ctx, member : discord.Member):
        await permit(self, ctx, member)

    @voice.command(name="reject", aliases=["deny"])
    async def voice_reject(self, ctx, member : discord.Member):
        await reject(self, ctx, member)

    @voice.command(name="limit")
    async def voice_limit(self, ctx, limit):
        await channellimit(self, ctx, limit)
                
    @voice.command(name="name")
    async def voice_name(self, ctx,*, name):
        await channelname(self, ctx, name)

    @voice.command(name="bitrate")
    async def voice_bitrate(self, ctx, bitrate:int):
        await bitratechannel(self, ctx, bitrate)

    @voice.command(name="help")
    async def voice_help(self, ctx):
        await help(self, ctx)

    @cog_ext.cog_slash(name="voice")
    async def _voice(self, ctx: SlashContext):
        """`!voice help` for a list of voice related commands"""
        pass

    @cog_ext.cog_subcommand(base="voice", name="setup", description="setup the voice functions to this discord")
    async def _voice_setup(self, ctx: SlashContext):
        await setup(self, ctx)
        
    @cog_ext.cog_subcommand(base="voice", name="lock", description="Lock your channel")
    async def _voice_lock(self, ctx: SlashContext):
        await lock(self, ctx)

    @cog_ext.cog_subcommand(base="voice", name="unlock", description="Unlock your channel")
    async def _voice_unlock(self, ctx: SlashContext):
        await unlock(self, ctx)

    @cog_ext.cog_subcommand(base="voice", name="permit", description="Give users permission to join your channel")
    async def _voice_permit(self, ctx: SlashContext, member: discord.Member):
        await permit(self, ctx, member)

    @cog_ext.cog_subcommand(base="voice", name="reject", description="Remove permission to join your channel and remove")
    async def _voice_reject(self, ctx: SlashContext, member: discord.Member):
        await reject(self, ctx, member)

    @cog_ext.cog_subcommand(base="voice", name="limit", description="Change your channel limit")
    async def _voice_limit(self, ctx: SlashContext, limit: int):
        await channellimit(self, ctx, limit)

    @cog_ext.cog_subcommand(base="voice", name="name", description="Change your channel name")
    async def _voice_name(self, ctx: SlashContext, name: str):
        await channelname(self, ctx, name)

    @cog_ext.cog_subcommand(base="voice", name="bitrate", description="Change your channel bitrate")
    async def _voice_bitrate(self, ctx: SlashContext, bitrate: int):
        await bitratechannel(self, ctx, bitrate)

    @cog_ext.cog_subcommand(base="voice", name="help", description="The list of commands for the voice functionality")
    async def _voice_help(self, ctx: SlashContext):
        await help(self, ctx)

def setup(bot):
    bot.add_cog(voice(bot))




