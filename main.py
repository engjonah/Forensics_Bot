import os
import keep_alive
import discord
from discord.ext import commands

client = commands.Bot(command_prefix = ('!'), help_command=None, description = 'Science Olympiad Forensics Bot')

@client.event
async def on_ready():
  print('Bot is ready.')
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))

@client.command(aliases=['h'])
#@commands.has_permissions(administrator=True)
async def help(ctx):
  await ctx.send('Hello! This is Forensics Bot, a bot to help you study for the Science Olympiad Foresnics Event.')


#bypass for repl time limit
keep_alive.keep_alive()


#Run bot with oauth token 
token = os.environ['token']
client.run(token)