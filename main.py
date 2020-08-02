import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import praw
import json
import sys
from datetime import datetime

#.env laden
load_dotenv()
TOKEN = os.getenv('discord_token')
client_id_var = os.getenv("reddit_client_id")
client_secret_var = os.getenv("reddit_client_secret")
user_agent_var = os.getenv("reddit_user_agent")


#bot command präfix
bot = commands.Bot(command_prefix='!')
bot.remove_command("help")
ffmpegpath = "res/ffmpeg.exe"
startTime = datetime.now()
print(startTime)

#reddit API laden
def Mainbot():
    reddit = praw.Reddit(client_id=client_id_var,client_secret=client_secret_var,user_agent=user_agent_var)
    post = reddit.subreddit('okbrudimongo').random()
    x = post.id

    with open('res/data.json', 'r') as e:
        eread = e.read()
        if x not in eread:
            with open('res/data.json', 'a') as f:
                json.dump(x, f)
                f.close()
        else:
            e.close()
    print(post.url + " " + "\n" + post.title + " " + "\n" + "https://reddit.com/r/okbrudimongo/comments/"+x)

    file = open("res/data.json", "r+")
    readfile = file.read()
    print(readfile.count('"'))
    if readfile.count('"')>100:
        file.truncate(0)
        print("data.json cleared")
    file.close()
    return(post.url + " " + "\n" + post.title + " " + "\n" + "https://reddit.com/r/okbrudimongo/comments/"+x)

# @bot.command(name="testname", help="testdescription")
# async def Test(ctx):
#     await ctx.send("Test")


@bot.command(help="zeigt genau das hier an.")
@commands.has_permissions(add_reactions=True,embed_links=True)
async def hilfe(ctx, *cog):
    # try:
    if not cog:
        """Cog listing.  What more?"""
        halp=discord.Embed(title='Verfügbare Wege der Volksverhetzung:',
                           description='')
        cogs_desc = ''

        for x in bot.cogs:
            cog_commands = bot.get_cog(x)
            test = cog_commands.get_commands()
            cogs_desc += ('\n**{}:** {}'.format(x,bot.cogs[x].__doc__)+'\n')
            for z in test:
                cogs_desc += (" - {} / {}  \n".format(str(z),z.help))
            cogs_desc += "---------"

        halp.add_field(name='Kategorien:',value=cogs_desc,inline=False)
        cmds_desc = ''
        Uncategorized_Command_Exist = False
        for y in bot.walk_commands():
            if not y.cog_name and not y.hidden:
                Uncategorized_Command_Exist = True
                cmds_desc += ('{}: {}'.format(y.name,y.help)+'\n')
        if Uncategorized_Command_Exist == True:
            halp.add_field(name='Diverses:',value=cmds_desc[0:len(cmds_desc)-1],inline=False)
        await ctx.message.add_reaction(emoji='✉')
        await ctx.message.author.send('',embed=halp)
    else:
        """Helps me remind you if you pass too many args."""
        if len(cog) > 1:
            halp = discord.Embed(title='Error!',description='That is way too many cogs!',color=discord.Color.red())
            await ctx.message.author.send('',embed=halp)
        else:
            """Command listing within a cog."""
            found = False
            for x in bot.cogs:
                for y in cog:
                    if x == y:
                        halp=discord.Embed(title=cog[0]+' Command Listing',description=bot.cogs[cog[0]].__doc__)
                        for c in bot.get_cog(y).get_commands():
                            if not c.hidden:
                                halp.add_field(name=c.name,value=c.help,inline=False)
                        found = True
            if not found:
                """Reminds you if that cog doesn't exist."""
                halp = discord.Embed(title='Error!',description='How do you even use "'+cog[0]+'"?',color=discord.Color.red())
            else:
                await ctx.message.add_reaction(emoji='✉')
            await ctx.message.author.send('',embed=halp)
    # except:
    #     await ctx.send("Excuse me, I can't send embeds.")



class Physik(commands.Cog):
    """
    Voll lustig lol rofl kek
    """

    def __init__(self, bot):
        self.bot = bot



    @commands.command(help="keckige witze")
    async def Wissen(self, ctx):
        await ctx.send(Mainbot())

    @commands.command(help="Ein Gruß vom Doktor")
    async def Willkommen(self, ctx):
        voice_channel = ctx.message.author.voice.channel
        if voice_channel != None:
            vc = await voice_channel.connect()
            vc.play(discord.FFmpegPCMAudio(source='res/welcome.mp3'))
            while vc.is_playing() == True:
                pass
            else:
                for x in bot.voice_clients:
                    if (x.guild == ctx.message.guild):
                        return await x.disconnect()

class Magie(commands.Cog):
    """
    Nur für den Führer!
    """
    def __init__(self, bot):
        self.bot = bot


    @commands.command(help="löscht letzte x Nachrichten im Kanal")
    @commands.has_permissions(administrator=True)
    async def Genozid(self, ctx, limit: int):
        await ctx.channel.purge(limit=limit)
        await ctx.send('Cleared by {}'.format(ctx.author.mention))
        await ctx.message.delete()


    @commands.command(help="Zeigt Deutsche Arbeitszeit des Doktors")
    async def Aufzeit(self, ctx):
        endTime = datetime.now()
        print(endTime)
        await ctx.send('Ich bin schon {} stationiert'.format(endTime - startTime))


@bot.event
async def on_ready():
    text_channel_list = []
    for guild in bot.guilds:
        for channel in guild.channels:
            if channel.category is not None:
                if "Text Channels" in str(channel.category):
                    text_channel_list.append(channel)

    print(f'{bot.user.name} has connected to Discord!')
    sys.stdout.flush()
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
        await message.channel.send(file=discord.File('res/mamamia.png'))
    if "wie viele" in str(message.content).lower():
        try:
            voice_channel = message.author.voice.channel
            print(voice_channel)
            sys.stdout.flush()
            vc = await voice_channel.connect()
            print(vc)
            sys.stdout.flush()
            vc.play(discord.FFmpegPCMAudio(source='res/alle.mp3'))
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
            vc.play(discord.FFmpegPCMAudio(source='res/ruegenwalder.mp3'))
            while vc.is_playing() == True:
                pass
            else:
                for x in bot.voice_clients:
                    if (x.guild == message.guild):
                        return await x.disconnect()
        except:
            await message.channel.send("Rügenwalder."+" "+str(message.author.mention))
    await bot.process_commands(message)


bot.add_cog(Physik(bot))
bot.add_cog(Magie(bot))
bot.run(TOKEN)
