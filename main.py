import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import praw
import json

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

class EnergetischeMatrix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """keckige mehmehs"""



    @commands.command(help="keckige witze")
    async def wissen(self, ctx):
        await ctx.send(Mainbot())

    @commands.command(help="Ein Gruß vom Doktor")
    async def willkommen(self, ctx):
        voice_channel = ctx.message.author.voice.channel
        if voice_channel != None:
            vc = await voice_channel.connect()
            vc.play(discord.FFmpegPCMAudio('welcome.mp3'), after=lambda e: print('done', e))
            while vc.is_playing() == True:
                pass
            else:
                for x in bot.voice_clients:
                    if (x.guild == ctx.message.guild):
                        return await x.disconnect()

class OberkommandoBefehle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="löscht letzte x Nachrichten im Kanal")
    @commands.has_permissions(administrator=True)
    async def magie(self, ctx, limit: int):
        await ctx.channel.purge(limit=limit)
        await ctx.send('Cleared by {}'.format(ctx.author.mention))
        await ctx.message.delete()



@bot.event
async def on_ready():
    text_channel_list = []
    for guild in bot.guilds:
        for channel in guild.channels:
            if channel.category is not None:
                if "Text Channels" in str(channel.category):
                    text_channel_list.append(channel)

    print(f'{bot.user.name} has connected to Discord!')
    await text_channel_list[0].send("Bin gelandet auf Aldebaran.")



# @bot.command()
# async def join(ctx):
#         channel = ctx.message.author.voice.channel
#         await channel.connect()
#         return channel.connect()

# @bot.command()
# async def leave(ctx):
#         print(bot.voice_clients)
#         for x in bot.voice_clients:
#             if(x.guild == ctx.message.guild):
#                 return await x.disconnect()


# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.errors.CheckFailure):
#         await ctx.send('You do not have the correct role for this command.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "mama mia" in str(message.content).lower():
        await message.channel.send(file=discord.File('mamamia.png'))
    if "wie viele" in str(message.content).lower():
        try:
            voice_channel = message.author.voice.channel
            vc = await voice_channel.connect()
            vc.play(discord.FFmpegPCMAudio('alle.mp3'), after=lambda e: print('done', e))
            while vc.is_playing() == True:
                pass
            else:
                for x in bot.voice_clients:
                    if (x.guild == message.guild):
                        return await x.disconnect()
        except:
            await message.channel.send("Alle."+" "+str(message.author.mention))
    if "teewurst?" in str(message.content).lower():
        try:
            voice_channel = message.author.voice.channel
            vc = await voice_channel.connect()
            vc.play(discord.FFmpegPCMAudio('ruegenwalder.mp3'), after=lambda e: print('done', e))
            while vc.is_playing() == True:
                pass
            else:
                for x in bot.voice_clients:
                    if (x.guild == message.guild):
                        return await x.disconnect()
        except:
            await message.channel.send("Rügenwalder."+" "+str(message.author.mention))
    await bot.process_commands(message)


bot.add_cog(EnergetischeMatrix(bot))
bot.add_cog(OberkommandoBefehle(bot))
bot.run(TOKEN)
