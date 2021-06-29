#for repl's secret token system
import os
#from keep_alive.py (command to keep web server up)
import keep_alive
#for discord api
import discord
from discord.ext import commands
#for dropbox api (download images)
import dropbox
#for image objects/processing
from PIL import Image 
import PIL
#for data stream conversion to 'file' for image processing
from io import BytesIO
#for random numbers
#import random 
#for answer data frame
import pandas as pd
#best answer out of 3
from collections import Counter

#dropbox setup
dropbox_token = os.environ['dropbox']
dbx = dropbox.Dropbox(dropbox_token)

#download image file from dropbox. this will be returned and sent into discord by another function. 

def download_image(dbx, file):
  _, f = dbx.files_download(path=file)
  f = f.content
  #print (f)
  return BytesIO(f)
   
#set up panda dataframe for answers
df = pd.read_csv('data/data.csv', header=0, dtype="string")
#print(df.to_string(index=False, header=True))

def get_fingerprint_info(row):
  info_list = df.iloc[row].values.tolist()
  print(info_list)
  return (info_list)


def write_fingerprint_info(list):
  #need line to alter row in df
  df.to_csv("data/data.csv", index=False, header=True)

#sets up bot. Command prefix as !, disables default help command. 
client = commands.Bot(command_prefix = ('!'), help_command=None)

#set's status to 'Listening to !help'. shows up under name
@client.event
async def on_ready():
  print('Bot is ready.')
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))

#help menu from !help
@client.command(aliases=['h'])
#@commands.has_permissions(administrator=True)
async def help(ctx):
  await ctx.send('Hello! This is Forensics Bot, a bot to help you study for the Science Olympiad Forensics Event.\n**This is still in development**\n!q for a fingerprint!\n!c to check answer\n!r to go back to the first finger\n!s to skip the question')

#get question
@client.command(aliases=['q'])
async def question(ctx):
  number = 0
  with open("data/fingerprint_counter.txt", "r") as file:
    number = int(file.readline())
  increment_finger()
  row = df.loc[number].astype(str).tolist()
  print(row)  
  while row[5]=="True":
    increment_finger()
    with open("data/fingerprint_counter.txt", "r") as file:
      number = int(file.readline())
    row = df.loc[number].astype(str).tolist() 
  person = int(number/10+1)
  finger = number%10
  if finger==0: #fix for me not using 0 based numbering when I named the files
    finger = 10
    person -=1
  file_name = str("/real_png/" + str(person) + "_" + str(finger) + ".png")
  print(file_name)
  img = Image.open(download_image(dbx, file_name))
  with BytesIO() as image_binary:
    img.save(image_binary, "PNG")
    image_binary.seek(0)
    await ctx.send(file=discord.File(fp=image_binary,filename="fingerprint.png"))
    if (finger in range(6)):
      await ctx.send("Left hand")
    elif (finger in range(6, 11)):
      await ctx.send("Right hand")

#function to move on to next finger. used after each display and when a finger is marked as 'skip'
def increment_finger():
  number=0
  with open("data/fingerprint_counter.txt", "r") as file:
    number = int(file.readline())
  with open("data/fingerprint_counter.txt", "w") as file:
    file.write(str(number+1))

#function to go back to finger 1. may be used to complete fingerprint annotations or start fresh.
@client.command(aliases=['r'])
async def reset(ctx):    
  with open("data/fingerprint_counter.txt", "w") as file:
    file.write(str(1))
  await ctx.send("Back to finger 1!")

#check answer
@client.command(aliases=['c'])
async def check(ctx, *x): 
  answers = ["plain arch", "tented arch", "radial loop", "ulnar loop", "plain whorl", "central pocket whorl", "accidental whorl", "double loop whorl"]
  answer = ' '.join(x).lower()
  print(answer)
  if answer in answers: 
    #edit csv row
    number=0
    with open("data/fingerprint_counter.txt", "r") as file:
      number = (int(file.readline())-2)
    row = df.loc[number].astype(str).tolist()
    if row[4]=="<NA>":
      for x in range(1,4):
        if(row[x]=="<NA>"):
          with open("data/fingerprint_counter.txt", "r") as file: 
            number = int(file.readline())-2 #1 for previous incrament, 1 for 0 based instead of 1 based
          df.at[number, "guess" + str(x)] = answer
          row = df.loc[number].astype(str).tolist()
          print(row)
          if ("<NA>" not in row[1:4]):
            counter = Counter(row[1:4])
            commons_list = counter.most_common(1)
            if len(commons_list) > 1:
              df.at[number, "skip"] = str(True)
            else:
              df.at[number, "answer"] = commons_list[0][0]
              df.at[number, "skip"] = str(False)
          row = df.loc[number].astype(str).tolist()
          print(row)
          df.to_csv("data/data.csv", index=False, header=True)
          await ctx.send(answer + ' written to file!')
          break
    else:
      if answer==row[4]:
        await ctx.send('Correct!')
      else:
        row = df.loc[number].astype(str).tolist()

        await ctx.send('Incorrect. The correct answer is ' + row[4])
  else:
    await ctx.send('Please reply with a correct fingerprint type.\nThe proper types are: ' + ", ".join(answers))
  df.to_csv("data/data.csv", index=False, header=True)

#command to mark fingerprint to skip    
@client.command(aliases=['s'])
async def skip(ctx):
  number=0
  with open("data/fingerprint_counter.txt", "r") as file:
    number = (int(file.readline())-2)
  df.at[number, "skip"] = str(True)
  df.to_csv("data/data.csv", index=False, header=True)
  await ctx.send('Marked finger as skip.')
  

#bypass for replit time limit - make a pingable webpage
keep_alive.keep_alive()


#Run bot with oauth token 
token = os.environ['token']
client.run(token)

