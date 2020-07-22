import os
import random
from dotenv import load_dotenv
import discord
from discord.ext import commands
import praw
import json
import urllib.request
import asyncio

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
    print(post.url + " " + "\n" + post.title + " " + "\n" + "https://reddit.com/r/okbrudimongo/comments/"+x)

    file = open("data.json","r+")
    readfile = file.read()
    print(readfile.count('"'))
    if readfile.count('"')>100:
        file.truncate(0)
        print("data.json cleared")
    file.close()
    return(post.url + " " + "\n" + post.title + " " + "\n" + "https://reddit.com/r/okbrudimongo/comments/"+x)

@bot.command(name="wissen", help="keckige witze")
async def okbrudimongo_post(ctx):
    await ctx.send(Mainbot())

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    channel = bot.get_channel(733248970771660825)
    await channel.send("Bin gelandet auf Aldebaran.")

@bot.command(name="Magie=Physik/Wollen", help="löscht letzte x nachrichten im kanal")
@commands.has_permissions(administrator=True)
async def clean(ctx, limit: int):
        await ctx.channel.purge(limit=limit)
        await ctx.send('Cleared by {}'.format(ctx.author.mention))
        await ctx.message.delete()

# @bot.command()
# async def join(ctx):
#         channel = ctx.message.author.voice.channel
#         await channel.connect()
#         return channel.connect()


@bot.command()
async def leave(ctx):
        print(bot.voice_clients)
        for x in bot.voice_clients:
            if(x.guild == ctx.message.guild):
                return await x.disconnect()

@bot.command()
async def alle(ctx):
    voice_channel = ctx.message.author.voice.channel
    if voice_channel != None:
        channel = voice_channel.name
        await ctx.send('User is in channel: ' + channel)
        vc = await voice_channel.connect()
        vc.play(discord.FFmpegPCMAudio('testing.mp3'), after=lambda e: print('done', e))
        while vc.is_playing() == True:
            pass
        else:
            for x in bot.voice_clients:
                 if (x.guild == ctx.message.guild):
                     return await x.disconnect()

    else:
        await ctx.send('User is not in a channel.')


# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.errors.CheckFailure):
#         await ctx.send('You do not have the correct role for this command.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content in ["wie viele?", "Wie viele?"]:
        await message.channel.send("Alle.")
    if "mama mia" in str(message.content).lower():
        await message.channel.send(file=discord.File('mamamia.png'))

    await bot.process_commands(message)



bot.run(TOKEN)
