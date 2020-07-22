import os
import random
from dotenv import load_dotenv
import discord
from discord.ext import commands
import praw
import json
import urllib.request
#.env laden
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#bot command präfix
bot = commands.Bot(command_prefix='!')

#reddit API laden
def Mainbot():
    reddit = praw.Reddit(client_id='x',client_secret='x',user_agent='x')
    post = reddit.subreddit('okbrudimongo').random()
    x = post.id


    with open('data.json', 'r') as e:
        eread = e.read()
        if x not in eread:
            with open('data.json', 'a') as f:
                json.dump(x, f)
                f.close()
        else:
            e.close()
            Mainbot()
    print(post.url + " " + "\n" + post.title + " " + "\n" + "https://reddit.com/r/okbrudimongo/comments/"+x)

    file = open("data.json","r+")
    readfile = file.read()
    print(readfile.count('"'))
    if readfile.count('"')>100:
        file.truncate(0)
        print("data.json cleared")
    file.close()
    return(post.url + " " + "\n" + post.title + " " + "\n" + "https://reddit.com/r/okbrudimongo/comments/"+x)

@bot.command(name="Elektrojude")
async def okbrudimongo_post(ctx):
    await ctx.send(Mainbot())

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(pass_context=True, name="Saubermachen", help="!clean x = letzte x nachrichten löschen")
@commands.has_permissions(administrator=True)
async def clean(ctx, limit: int):
        await ctx.channel.purge(limit=limit)
        await ctx.send('Cleared by {}'.format(ctx.author.mention))
        await ctx.message.delete()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content in ["wie viele?", "Wie viele?"]:
        await message.channel.send("Alle.")
    await bot.process_commands(message)


bot.run(TOKEN)
