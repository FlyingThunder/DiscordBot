import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import praw
import json
import sys
from datetime import datetime
from riotwatcher import LolWatcher, ApiError
import urllib.request
import youtube_dl

#.env laden
load_dotenv()
TOKEN = os.getenv('discord_token')
client_id_var = os.getenv("reddit_client_id")
client_secret_var = os.getenv("reddit_client_secret")
user_agent_var = os.getenv("reddit_user_agent")
riot_api_key = os.getenv("riot_api_key")

watcher = LolWatcher(riot_api_key)
my_region = 'euw1'

files = os.listdir('res')
audiofiles = []
for x in files:
    if ('.mp3' or '.wav') in str(x):
        audiofiles.append(x)
print(audiofiles)



#bot command präfix
bot = commands.Bot(command_prefix='!',case_insensitive=True)
bot.remove_command("help")
ffmpegpath = "res/ffmpeg.exe"
startTime = datetime.now()
print(startTime)

#reddit API laden

def champLookup(champId):
    latest = watcher.data_dragon.versions_for_region(my_region)['n']['champion']
    static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')
    champ_dict = {}
    for key in static_champ_list['data']:
        row = static_champ_list['data'][key]
        champ_dict[row['key']] = row['id']

    return champ_dict[str(champId)]

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

def Bruder(name):
    # latest = watcher.data_dragon.versions_for_region(my_region)['n']['champion']
    # static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')
    # champ_dict = {}
    # for key in static_champ_list['data']:
    #     row = static_champ_list['data'][key]
    #     champ_dict[row['key']] = row['id']

    me = watcher.summoner.by_name(my_region, name)

    gametype = "Unknown"
    champion = None
    starttime = None
    status = None

    try:
        playerinstance = watcher.spectator.by_summoner(my_region, me['id'])
        matchstart = str(playerinstance['gameStartTime'])[:-3]
        participants = playerinstance['participants']

        for x in participants:
            if x['summonerName'] == name:
                champion = champLookup(str(x['championId']))



        status = "Ingame"

        if str(playerinstance['gameQueueConfigId']) == "400":
            gametype = "5v5 Normal Draft"
        if str(playerinstance['gameQueueConfigId']) == "420":
            gametype = "5v5 Ranked Solo/Duo"
        if str(playerinstance['gameQueueConfigId']) == "440":
            gametype = "5v5 Ranked Flex"
        if str(playerinstance['gameQueueConfigId']) == "450":
            gametype = "ARAM"
        if str(playerinstance['gameQueueConfigId']) == "700":
            gametype = "Clash"



        starttime = datetime.fromtimestamp(int(matchstart)).strftime('%Y-%m-%d %H:%M:%S')

    except:
        status = "Not ingame"
    return (name, status, gametype, champion, starttime)

def Last_10_games(name):
    me = watcher.summoner.by_name(my_region, name)
    matches = watcher.match.matchlist_by_account(my_region, me['accountId'])
    x = matches['matches'][:10]
    matchlist = []
    for a in x:
        matchlist.append(watcher.match.by_id(my_region, a['gameId']))

    output = []
    letzte10embed = discord.Embed(title='Jason Statistikschinken')

    for y in matchlist:
        print("New game")
        for x in y['participantIdentities']:
            if x['player']['summonerName'] == name:
                participantId = x['participantId']
                for z in y['participants']:
                    if z['participantId'] == participantId:
                        arguments = []
                        arguments.append(champLookup(z['championId']))
                        if z['stats']['win'] == False:
                            arguments.append("Loss")
                        elif z['stats']['win'] == True:
                            arguments.append("Win")
                        arguments.append(str(z['stats']['kills']) + "/" + str(z['stats']['deaths']) + "/" + str(
                            z['stats']['assists']))
                        if str(y['queueId']) == "400":
                            arguments.append("5v5 Normal Draft")
                        if str(y['queueId']) == "420":
                            arguments.append("5v5 Ranked Solo/Duo")
                        if str(y['queueId']) == "440":
                            arguments.append("5v5 Ranked Flex")
                        if str(y['queueId']) == "450":
                            arguments.append("ARAM")
                        if str(y['queueId']) == "700":
                            arguments.append("Clash")
                        if z['stats']['win'] == False:
                            letzte10embed.add_field(name=":monkey:", value=str(arguments), inline=False)
                        elif z['stats']['win'] == True:
                            letzte10embed.add_field(name=":star_of_david:", value=str(arguments), inline=False)


    return(letzte10embed)

async def Labern(audiofile, message):
   voice_channel = message.author.voice.channel
   vc = await voice_channel.connect()
   vc.play(discord.FFmpegPCMAudio(source='res/{}.mp3'.format(audiofile)))
   while vc.is_playing() == True:
       pass
   else:
       for x in bot.voice_clients:
           if (x.guild == message.guild):
               return await x.disconnect()


# @bot.command(name="testname", help="testdescription")
# async def Test(ctx):
#     await ctx.send("Test")


@bot.command(help="zeigt genau das hier an.")
@commands.has_permissions(add_reactions=True,embed_links=True)
async def Hilfe(ctx, *cog):
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
                cogs_desc += ("\n - {} \|\|\| {} \n".format(str(z),z.help))
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
        await ctx.message.channel.send('',embed=halp)
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
            halp.add_field(name='Voicechat Befehle:', value='"Wie viele", "Teewurst?", "Alarm", "Wer ist das"', inline=False)
            await ctx.message.channel.send('',embed=halp)
    # except:
    #     await ctx.send("Excuse me, I can't send embeds.")



class Physik(commands.Cog):
    """
    Sinnlose dumme Scheiße
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Youtube -> mp3 download für Audiobefehl")
    async def add_youtubeaudio(self, ctx, url, name=None):
        ydl_opts = {
            'outtmpl': 'test.mp3',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        os.rename('test.mp3', 'res/'+str(name)+'.mp3')

        await ctx.send("YT Video " + str(url) + " runtergeladen unter dem Namen: " + str(name))


    @commands.command(help="stats vong letzte 10 spiele her")
    async def Letzte10(self, ctx, argument):
        await ctx.send('', embed=Last_10_games(name=argument))

    @commands.command(help="Dateinamen OHNE '.mp3' an den Befehl anhängen! \n" + str(audiofiles))
    async def Sag(self, ctx, argument):
        play = argument
        try:
            print(play)
            await Labern(audiofile=play, message=ctx.message)
        except:
            await ctx.send("Spast" + " " + str(ctx.author.mention))

    @commands.command(help="URL der Audiodatei (mp3) anhängen + Name des Outputs")
    async def add_audiofile(self, ctx, link, name=None):
        print(link)
        if name == None:
            urllib.request.urlretrieve(link, "res/"+str(link.split("/")[-1]))
        else:
            urllib.request.urlretrieve(link, "res/" + str(name) + ".mp3")
        await ctx.send("Audiodatei " + str(link.split("/")[-1]) + " hinzugefügt")

    @commands.command(help="SEID IHR BEREIT KINDER?")
    async def Squad(self, ctx):
        squad_info = discord.Embed(title='MELDET EUCH ZUM DIENST!',description='BUBENSTATUS')

        mongos_list = {"Peschko": "DiggaShishaBar", "Simon": "HiSim", "Felix": "Letax", "Johann": "Gammanus",
                       "Andrê": "Azzazzin"}
        for x in mongos_list.keys():
            y = mongos_list[x]
            data = Bruder(name=y)
            print(data)
            if data[1] == "Ingame":
                playerinfo = "ist in einem {} mit {} seit {} auf dem Account {}".format(data[2],data[3],data[4].split(" ")[1],data[0])
            else:
                playerinfo = "ist nicht ingame"
            squad_info.add_field(name=str(x), value=playerinfo, inline=False)


        await ctx.send('', embed=squad_info)

    @commands.command(help="keckige witze")
    async def Wissen(self, ctx):
        await ctx.send(Mainbot())

class Magie(commands.Cog):
    """
    Weniger sinnlos, trotzdem Scheiße
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

    print(f'{bot.user.name} has connected to {guild}')
    sys.stdout.flush()
    await text_channel_list[0].send("Bin gelandet auf Aldebaran.")



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
    # if "rügenwalder mühlenfest" in str(message.content).lower():
    #     try:
    #         voice_channel = message.author.voice.channel
    #         vc = await voice_channel.connect()
    #         vc.play(discord.FFmpegPCMAudio(source='res/teewurst_jingle.mp3'))
    #         while vc.is_playing() == True:
    #             pass
    #         else:
    #             for x in bot.voice_clients:
    #                 if (x.guild == message.guild):
    #                     return await x.disconnect()
    #     except:
    #         await message.channel.send("Rügenwalder Mühlenfest!"+" "+str(message.author.mention))
    # if "alarm" in str(message.content).lower():
    #     try:
    #         voice_channel = message.author.voice.channel
    #         vc = await voice_channel.connect()
    #         vc.play(discord.FFmpegPCMAudio(source='res/er_kommt.mp3'))
    #         while vc.is_playing() == True:
    #             pass
    #         else:
    #             for x in bot.voice_clients:
    #                 if (x.guild == message.guild):
    #                     return await x.disconnect()
    #     except:
    #         await message.channel.send("Er kommt!"+" "+str(message.author.mention))
    # if "wie viele" in str(message.content).lower():
    #     try:
    #         voice_channel = message.author.voice.channel
    #         vc = await voice_channel.connect()
    #         vc.play(discord.FFmpegPCMAudio(source='res/alle.mp3'))
    #         while vc.is_playing() == True:
    #             pass
    #         else:
    #             for x in bot.voice_clients:
    #                 if (x.guild == message.guild):
    #                     return await x.disconnect()
    #     except:
    #         await message.channel.send("Alle."+" "+str(message.author.mention))
    # if "teewurst?" in str(message.content).lower():
    #     try:
    #         voice_channel = message.author.voice.channel
    #         vc = await voice_channel.connect()
    #         vc.play(discord.FFmpegPCMAudio(source='res/ruegenwalder.mp3'))
    #         while vc.is_playing() == True:
    #             pass
    #         else:
    #             for x in bot.voice_clients:
    #                 if (x.guild == message.guild):
    #                     return await x.disconnect()
    #     except:
    #         await message.channel.send("Rügenwalder."+" "+str(message.author.mention))
    # if "wer ist das" in str(message.content).lower():
    #     try:
    #         voice_channel = message.author.voice.channel
    #         vc = await voice_channel.connect()
    #         vc.play(discord.FFmpegPCMAudio(source='res/wer_ist_das.mp3'))
    #         while vc.is_playing() == True:
    #             pass
    #         else:
    #             for x in bot.voice_clients:
    #                 if (x.guild == message.guild):
    #                     return await x.disconnect()
    #     except:
    #         await message.channel.send("Wer ist das?"+" "+str(message.author.mention))
    # if "achtarmiger" in str(message.content).lower():
    #     try:
    #         voice_channel = message.author.voice.channel
    #         vc = await voice_channel.connect()
    #         vc.play(discord.FFmpegPCMAudio(source='res/achtarmiger.mp3'))
    #         while vc.is_playing() == True:
    #             pass
    #         else:
    #             for x in bot.voice_clients:
    #                 if (x.guild == message.guild):
    #                     return await x.disconnect()
    #     except:
    #         await message.channel.send("@Gammanus macht Stulle."+" "+str(message.author.mention))
    await bot.process_commands(message)


bot.add_cog(Physik(bot))
bot.add_cog(Magie(bot))
bot.run(TOKEN)
