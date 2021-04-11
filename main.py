"""discord api connection"""
import discord
from discord import Game
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
from discord_slash import SlashCommand
import asyncio
from cogs.api.mongo import Document
import motor.motor_asyncio

# bot token you can get from: https://discord.com/developers/applications/
TOKEN = ""
# create a free mongodb data base here: https://www.mongodb.com/3 and connect it
MONGODBCONNECTION = ""

intents = discord.Intents.default()
intents.members = True
#bot = commands.Bot(command_prefix='!')
bot = AutoShardedBot(command_prefix="!", intents=intents)
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True) # Declares slash commands through the client.

# # uncomment after you setup the file within cogs/cogname to use it:

# # our report system: https://discord.com/channels/513749917567811586/794188772237377586/794199015025278979
# bot.load_extension("cogs.bob_reports")

# # creates a welcome message if someone joins and gives the bros army role
# bot.load_extension("cogs.bob_only")

# # makes temporary voice channels that automaticly get removed when its empty
# bot.load_extension("cogs.voice")

# # give people a role by clicking a emoji: https://discord.com/channels/513749917567811586/794133368291328010/794675751127220225
# bot.load_extension("cogs.bob_firestarters")

# # give people a role by clicking a emoji, also allows admins to add emojis: https://discord.com/channels/513749917567811586/795014651402125352/795015094132015144
# bot.load_extension("cogs.bob_games_we_play")

# # our !suggest command
# bot.load_extension("cogs.bob_suggestions")

# # logs if someone bans a player to a channel
# bot.load_extension("cogs.bob_logs")

@bot.event
async def on_ready():
    print("bot started \n")
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(MONGODBCONNECTION))
    bot.db = bot.mongo["commanager"]
    # where to save everything in database
    bot.config = Document(bot.db, 'config') # games-we-play db
    bot.suggestions = Document(bot.db, 'suggestions') # suggestions db
    
    bot.voiceGuild = Document(bot.db, 'voiceGuild') # voice guild db
    bot.voiceGuildSettings = Document(bot.db, 'voiceGuildSettings') # voice guild db
    bot.voiceUserSettings = Document(bot.db, 'voiceUserSettings') # voice guild db
    bot.voiceChannel = Document(bot.db, 'voiceChannel') # voice guild db
    
    print("Initialized Database")
    print(f"Connected on {str(len(bot.guilds))} server(s)")
    try:
        while True:
            await bot.change_presence(activity=discord.Game(f"in {str(len(bot.guilds))} servers"))
            await asyncio.sleep(900)
    except Exception as e:
        print(e)

#dont give a error if a command doesn't exist
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        return
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(color=0xe74c3c, description="Your not allowed to use this command")
        await ctx.send(embed=embed)
    raise error
#run the bot
bot.run(TOKEN)
