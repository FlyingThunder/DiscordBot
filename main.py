import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import praw
import json
import sys
from datetime import datetime
from riotwatcher import LolWatcher, TftWatcher
import urllib.request
#import youtube_dlc
import youtube_dl
from audioclipextractor import AudioClipExtractor
import dropbox
from collections import Counter
import random
import requests
from PIL import Image

# .env laden
load_dotenv()
TOKEN = os.getenv('discord_token')
client_id_var = os.getenv("reddit_client_id")
client_secret_var = os.getenv("reddit_client_secret")
user_agent_var = os.getenv("reddit_user_agent")
riot_api_key = os.getenv("riot_api_key")
dropbox_key = os.getenv("dropbox_key")
tft_api_key = os.getenv("tft_api_key")

watcher = LolWatcher(riot_api_key)
tftwatcher = TftWatcher(tft_api_key)
my_region = 'euw1'
dbx = dropbox.Dropbox(dropbox_key)

environment = "heroku" #local/heroku

# bot command präfix
bot = commands.Bot(command_prefix='!', case_insensitive=True)
bot.remove_command("help")
ffmpegpath = "res/ffmpeg.exe"
startTime = datetime.now()
print(startTime)


def dropbox_upload(filename):
    audiofiles_dropbox = []
    dropbox_filescan = dbx.files_list_folder("/discordbotmp3s")
    for x in dropbox_filescan.entries:
        audiofiles_dropbox.append(x.name.lower())

    x = str(filename).lower() + ".mp3"
    if x not in audiofiles_dropbox:
        f = open('res/mp3s/{}'.format(x.lower()), 'rb')
        print("Datei noch nicht vorhanden. Lade nach DropBox hoch.")
        dbx.files_upload(f.read(), "/DiscordBotMp3s/{}".format(x))
        return "upload"
    else:
        # print(os.path.getsize('res/mp3s/{}'.format(x)))
        # print(dbx.files_get_metadata("/discordbotmp3s/{}".format(x)).size)
        if os.path.getsize('res/mp3s/{}'.format(x.lower())) != dbx.files_get_metadata("/discordbotmp3s/{}".format(x)).size:
            print("Datei vorhanden, Metadaten nicht identisch. Überschreibe auf DropBox.")
            f = open('res/mp3s/{}'.format(x.lower()), 'rb')
            dbx.files_delete_v2("/DiscordBotMp3s/{}".format(x))
            dbx.files_upload(f.read(), "/DiscordBotMp3s/{}".format(x))
            return "overwrite"
        else:
            f = open('res/mp3s/{}'.format(x.lower()), 'rb')
            dbx.files_delete_v2("/DiscordBotMp3s/{}".format(x))
            dbx.files_upload(f.read(), "/DiscordBotMp3s/{}".format(x))
            return "upload_same"

def dropbox_download():
    audiofiles_dropbox = []
    dropbox_filescan = dbx.files_list_folder("/discordbotmp3s")
    for x in dropbox_filescan.entries:
        audiofiles_dropbox.append(x.name)
    print(audiofiles_dropbox)

    mp3_files = os.listdir("res/mp3s/")

    for y in audiofiles_dropbox:
        if y not in mp3_files:
            with open("res/mp3s/{}".format(y.lower()), "wb") as f:
                metadata, res = dbx.files_download(path="/DiscordBotMp3s/{}".format(y))
                f.write(res.content)

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        pass

# def champLookup(champId):
#     latest = watcher.data_dragon.versions_for_region(my_region)['n']['champion']
#     static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')
#     champ_dict = {}
#     for key in static_champ_list['data']:
#         row = static_champ_list['data'][key]
#         champ_dict[row['key']] = row['id']
#
#     return champ_dict[str(champId)]

def Mainbot():
    reddit = praw.Reddit(client_id=client_id_var,client_secret=client_secret_var,user_agent=user_agent_var)
    post = reddit.subreddit('okbrudimongo').random()
    x = post.id

    with open('res/reddit_posts.json', 'r') as e:
        eread = e.read()
        if x not in eread:
            with open('res/reddit_posts.json', 'a') as f:
                json.dump(x, f)
    print(post.url + " " + "\n" + post.title + " " + "\n" + "https://reddit.com/r/okbrudimongo/comments/"+x)

    with open("res/reddit_posts.json", "r+") as file:
        readfile = file.read()
        print(readfile.count('"'))
        if readfile.count('"')>100:
            file.truncate(0)
            print("reddit_posts.json cleared")
    return(post.url + " " + "\n" + post.title + " " + "\n" + "https://reddit.com/r/okbrudimongo/comments/"+x)

# def Bruder(name):
#     # latest = watcher.data_dragon.versions_for_region(my_region)['n']['champion']
#     # static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')
#     # champ_dict = {}
#     # for key in static_champ_list['data']:
#     #     row = static_champ_list['data'][key]
#     #     champ_dict[row['key']] = row['id']
#
#     me = watcher.summoner.by_name(my_region, name)
#
#     gametype = "Unknown"
#     champion = None
#     starttime = None
#     status = None
#
#     try:
#         playerinstance = watcher.spectator.by_summoner(my_region, me['id'])
#         matchstart = str(playerinstance['gameStartTime'])[:-3]
#         participants = playerinstance['participants']
#
#         for x in participants:
#             if x['summonerName'] == name:
#                 champion = champLookup(str(x['championId']))
#
#         print(playerinstance)
#
#         status = "Ingame"
#         if str(playerinstance['gameType']) == "CUSTOM_GAME":
#             gametype = "Customgame"
#         else:
#             if str(playerinstance['gameQueueConfigId']) == "400":
#                 gametype = "5v5 Normal Draft"
#             elif str(playerinstance['gameQueueConfigId']) == "420":
#                 gametype = "5v5 Ranked Solo/Duo"
#             elif str(playerinstance['gameQueueConfigId']) == "440":
#                 gametype = "5v5 Ranked Flex"
#             elif str(playerinstance['gameQueueConfigId']) == "450":
#                 gametype = "ARAM"
#             elif str(playerinstance['gameQueueConfigId']) == "700":
#                 gametype = "Clash"
#             else:
#                 gametype = "Unbekannt"
#
#
#
#         starttime = datetime.fromtimestamp(int(matchstart)).strftime('%Y-%m-%d %H:%M:%S')
#
#     except:
#         status = "Not ingame"
#     return (name, status, gametype, champion, starttime)

# def Last_10_games(name):
#     me = watcher.summoner.by_name(my_region, name)
#     matches = watcher.match.matchlist_by_account(my_region, me['accountId'])
#     x = matches['matches'][:10]
#     matchlist = []
#     for a in x:
#         matchlist.append(watcher.match.by_id(my_region, a['gameId']))
#
#     output = []
#     letzte10embed = discord.Embed(title='Jason Statistikschinken')
#
#     for y in matchlist:
#         print("New game")
#         for x in y['participantIdentities']:
#             if x['player']['summonerName'] == name:
#                 participantId = x['participantId']
#                 for z in y['participants']:
#                     if z['participantId'] == participantId:
#                         arguments = []
#                         arguments.append(champLookup(z['championId']))
#                         if z['stats']['win'] == False:
#                             arguments.append("Loss")
#                         elif z['stats']['win'] == True:
#                             arguments.append("Win")
#                         arguments.append(str(z['stats']['kills']) + "/" + str(z['stats']['deaths']) + "/" + str(
#                             z['stats']['assists']))
#                         if str(y['queueId']) == "400":
#                             arguments.append("5v5 Normal Draft")
#                         if str(y['queueId']) == "420":
#                             arguments.append("5v5 Ranked Solo/Duo")
#                         if str(y['queueId']) == "440":
#                             arguments.append("5v5 Ranked Flex")
#                         if str(y['queueId']) == "450":
#                             arguments.append("ARAM")
#                         if str(y['queueId']) == "700":
#                             arguments.append("Clash")
#                         if z['stats']['win'] == False:
#                             letzte10embed.add_field(name=":monkey:", value=str(arguments), inline=False)
#                         elif z['stats']['win'] == True:
#                             letzte10embed.add_field(name=":star_of_david:", value=str(arguments), inline=False)
#
#
#     return(letzte10embed)

async def Labern(message, audiofile, volume):
    #if os.path.exists("res/mp3s/{}.mp3".format(audiofile)):
    if volume is None:
        voice_channel = message.author.voice.channel
        vc = await voice_channel.connect()
        print(f"spiele audiofile {audiofile.lower()} ab")
        vc.play(discord.FFmpegPCMAudio('res/mp3s/{}.mp3'.format(audiofile.lower())))
        while vc.is_playing() == True:
            pass
        else:
            for x in bot.voice_clients:
                if (x.guild == message.guild):
                    await x.disconnect()

    else:
        voice_channel = message.author.voice.channel
        vc = await voice_channel.connect()
        vc.play(discord.FFmpegPCMAudio('res/mp3s/{}.mp3'.format(audiofile.lower())))
        vc.source = discord.PCMVolumeTransformer(vc.source)
        vc.source.volume = float(volume)
        print(volume)
        while vc.is_playing() == True:
            pass
        else:
            for x in bot.voice_clients:
                if (x.guild == message.guild):
                    await x.disconnect()

    while vc.is_playing() == True:
        pass
    else:
        for x in bot.voice_clients:
            if (x.guild == message.guild):
                await x.disconnect()
    #else:
    #    return("Exception: File not found")


# @bot.command(name="testname", help="testdescription")
# async def Test(ctx):
#     await ctx.send("Test")


@bot.command(help="zeigt genau das hier an.")
@commands.has_permissions(add_reactions=True,embed_links=True)
async def Hilfe(ctx, *cog):
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
            await ctx.message.channel.send('',embed=halp)




class Physik(commands.Cog):
    """
    Sinnlose dumme Scheiße
    """

    def __init__(self, bot):
        self.bot = bot

    # @commands.command(help="stats vong letzte 10 spiele her")
    # async def Letzte10(self, ctx, argument):
    #     await ctx.send('', embed=Last_10_games(name=argument))

    # @commands.command(help="TFT Testshit")
    # async def TFT(self, ctx, name, count=1):
    #     testvar = tftwatcher.summoner.by_name("euw1", name)
    #     puuid = testvar['puuid']
    #     match = tftwatcher.match.by_puuid("europe", puuid, count)
    #     x = 0
    #     while x < count:
    #         matchdetail = tftwatcher.match.by_id("europe", match[x])
    #         index_of_summoner = matchdetail['metadata']['participants'].index(puuid)
    #         metadata_of_summoner = matchdetail['info']['participants'][index_of_summoner]
    #         rounds = metadata_of_summoner['last_round']
    #         level = metadata_of_summoner['level']
    #         place = metadata_of_summoner['placement']
    #         killed = metadata_of_summoner['players_eliminated']
    #         total_damage = metadata_of_summoner['total_damage_to_players']
    #         champions = []
    #         for z in metadata_of_summoner['units']:
    #             champions.append({z['character_id']: z['items']})
    #         traits = []
    #         x += 1
    #         for y in metadata_of_summoner['traits']:
    #             traits.append({y['name']: y['num_units']})
    #         match_info_list = {'Platz': place,
    #                            'Level': level,
    #                            'Runden': rounds,
    #                            'Killed': killed,
    #                            'Damage': total_damage,
    #                            'Traits': traits,
    #                            'Champions': champions}
    #
    #         with open('res/items.json') as json_file:
    #             data = json.load(json_file)
    #             itemdict = {}
    #             for b in data:
    #                 itemdict[str(b['id'])] = str(b['name'])
    #
    #         newchamplist = []
    #         for a in match_info_list['Champions']:
    #             for key, value in a.items():
    #                 newitemlist = []
    #                 if value:
    #                     for c in value:
    #                         newitemlist.append(itemdict[str(c)])
    #                 newchamplist.append({key: newitemlist})
    #
    #         match_info_list['Champions'] = newchamplist
    #         print("Letzte {} Matches für {} von {} angefordert".format(count,name,ctx.author))
    #         await ctx.send(match_info_list)
    @commands.command(help="Teste deinen Glauben")
    async def Resolve(self, ctx):

        author = ctx.message.author
        pfp = author.avatar_url
        response = requests.get(pfp)
        with open("res/pillow/temp_pfp.png", "wb+") as file:
            file.write(response.content)

        #roll random 25/75 virtue / affliction
        virtues = {"stalwart": "Many fall in the face of chaos; but not this one, not today.",
                   "courageous": "A moment of valor shines brightest against a backdrop of despair.",
                   "focused": "A moment of clarity in the eye of the storm...",
                   "powerful": "Anger is power - unleash it!",
                   "vigorous": "Adversity can foster hope, and resilience."}

        affliction = {"fearful": "Fear and frailty finally claim their due.",
                      "paranoid": "The walls close in, the shadows whisper of conspiracy!",
                      "selfish": "Self-preservation is paramount - at any cost!",
                      "masochistic": "Those who covet injury find it in no short supply.",
                      "abusive": "Frustration and fury, more destructive than a hundred cannons.",
                      "hopeless": "There can be no hope in this hell, no hope at all.",
                      "irrational": "Reeling, gasping, taken over the edge into madness!"}

        vlist = list(virtues.items())
        alist = list(affliction.items())

        positiv_negativ = random.randint(0, 100)
        print(positiv_negativ)
        if positiv_negativ < 25:
            randresult = random.choice(vlist)
            image = "res/pillow/" + str(randresult[0]) + ".jpg"
            text = randresult[1]

        elif positiv_negativ >= 25:
            randresult = random.choice(alist)
            image = "res/pillow/" + str(randresult[0]) + ".jpg"
            text = randresult[1]
        else:
            image = "res/pillow/focused.jpg"
            text = "A moment of clarity in the eye of the storm..."
            print("RandInt failed")

        print(image + " + " + text)

        with Image.open("res/pillow/temp_pfp.png") as im:
            im_resized = im.resize((350, 350))
            im_resized.save("res/pillow/temp_pfp.png", "png")

        background = Image.open(image)
        overlay = Image.open("res/pillow/temp_pfp.png")
        background = background.convert("RGBA")
        overlay = overlay.convert("RGBA")
        new_img = Image.blend(background, overlay, 0.5)
        new_img.save("res/pillow/temp_result.png", "PNG")


        await ctx.send(file=discord.File(r"res/pillow/temp_result.png"))
        await ctx.send(text)


        try:
            os.remove("res/pillow/temp_pfp.png")
            os.remove("res/pillow/temp_result.png")
        except:
            print("File does not exist")


    @commands.command(help="Volume dazu angeben")
    async def Random(self, ctx, argument=1):
        file = random.choice(os.listdir("res/mp3s/"))
        cutfile = file.replace(".mp3","")

        if argument == "random":
            volume = random.randint(0,50)

        await Labern(audiofile=cutfile, message=ctx.message, volume=volume)

    @commands.command(help="Dateinahmen anhängen ODER url von Youtubevideo")
    async def Sag(self, ctx, argument=None, *args):
        url = None
        play = None

        for x in args:
            if "@" in str(x):
                getuser = ctx.message.server.get_member(str(x))
                ctx.message.author = getuser


        if argument:
            if "http" in argument:
                url = argument
            else:
                play = argument
                try:
                    os.path.getsize('res/mp3s/{}.mp3'.format(argument.lower()))
                except:
                    pass

            if play:
                #try:
                audiostat_list = []
                if len(args) > 1:
                    await ctx.send("Guck mal !mp3s und überleg ob du behindert bist")
                    return
                elif len(args) == 1:
                    await Labern(audiofile=play, message=ctx.message, volume=args[0])
                else:
                    await Labern(audiofile=play, message=ctx.message, volume=None)

                filelist = []
                for file in os.listdir('res/mp3s/'):
                    filelist.append(file.lower())
                if f'{play}.mp3'.lower() in filelist:
                    print("file exists, writing in mp3stats")
                    with open('res/mp3s_stats.txt', 'r', encoding="utf-8") as e:
                        try:
                            content = json.load(e)
                            for x in content:
                                audiostat_list.append(x)
                        except:
                            print("Datei ist noch leer")
                    data = {"Audiofile":play.lower(),"Zeit":str(datetime.now()),"Author":str(ctx.author)}
                    audiostat_list.append(data)
                    print(data)
                    with open('res/mp3s_stats.txt', 'w', encoding="utf-8") as f:
                        json.dump(audiostat_list, f, ensure_ascii=False)
                    with open('res/mp3s_stats.txt', 'rb') as g:
                        try:
                            dbx.files_delete_v2("/mp3s_stats.txt")
                        except:
                            pass
                        dbx.files_upload(g.read(), "/mp3s_stats.txt")
                else:
                    print("file does not exist, searching simmilar names")
                    files = os.listdir('res/mp3s/')
                    matchedfiles = [extension for extension in files if (argument.lower() in extension.lower())]
                    if matchedfiles:
                        await ctx.send(f"Meinst du {matchedfiles}")
                    else:
                        await ctx.send("Datei konnte nicht gefunden werden")

            elif url:
                if len(args) == 0: #ganzes video, ohne volume
                    await Magie.add_youtubeaudio(Magie(bot), url=url, ctx=ctx, name="temp_file", temp=True)
                    try:
                        print("Audiodatei wird abgespielt: " + "temp_file" + " von: " + str(ctx.author))
                        await Labern(audiofile="temp_file", message=ctx.message, volume=None)
                    except Exception as e:
                        await ctx.send("Spast" + " " + ctx.author.mention)
                        print("Exception:" + str(e))
                    print("Audiodatei wird aus Youtubevideo abgespielt und anschließend gelöscht: " + url + "von: " + str(ctx.author))
                if len(args) == 1: #ganzes video, mit volume
                    await Magie.add_youtubeaudio(Magie(bot), url=url, ctx=ctx, name="temp_file", temp=True)
                    try:
                        print("Audiodatei wird abgespielt: " + "temp_file" + " von: " + str(ctx.author))
                        await Labern(audiofile="temp_file", message=ctx.message, volume=args[0])
                    except Exception as e:
                        await ctx.send("Spast" + " " + ctx.author.mention)
                        print("Exception:" + str(e))
                    print("Audiodatei wird aus Youtubevideo abgespielt und anschließend gelöscht: " + url + "von: " + str(ctx.author))
                elif len(args) == 2: #start + end
                    await Magie.add_youtubeaudio(Magie(bot), url=url, ctx=ctx, name="temp_file", start=args[0], end=args[1], temp=True)
                    try:
                        print("Audiodatei wird abgespielt: " + "temp_file" + " von: " + str(ctx.author))
                        await Labern(audiofile="temp_file", message=ctx.message, volume=None)
                    except Exception as e:
                        await ctx.send("Spast" + " " + ctx.author.mention)
                        print("Exception:" + str(e))
                    print("Audiodatei wird aus Youtubevideo abgespielt und anschließend gelöscht: " + url + "Zeit: " + str(args[0]) + " / " + str(args[1]) +  " von: " + str(ctx.author))
                elif len(args) == 3: #start+end+volume
                    await Magie.add_youtubeaudio(Magie(bot), url=url, ctx=ctx, name="temp_file", start=args[0], end=args[1], temp=True)
                    try:
                        print("Audiodatei wird abgespielt: " + "temp_file" + " von: " + str(ctx.author))
                        await Labern(audiofile="temp_file", message=ctx.message, volume=args[2])
                    except Exception as e:
                        await ctx.send("Spast" + " " + ctx.author.mention)
                        print("Exception:" + str(e))
                    print("Audiodatei wird aus Youtubevideo abgespielt und anschließend gelöscht: " + url + "Zeit: " + str(args[0]) + " / " + str(args[1]) +  " von: " + str(ctx.author))
                try:
                    os.remove('res/mp3s/temp_file.mp3')
                except:
                    print("Scheint nicht zu existieren?")
        else:
            await ctx.send("Dumm oder was?")

    # @Sag.error
    # async def Sag_handler(self, ctx, error):
    #     print("Exception /// Errorhandler" + str(error))
    #
    #     if "FileNotFoundError" in str(error):
    #         print("Datei konnte nicht gefunden werden")
    #         await ctx.send("Datei konnte nicht gefunden werden")
    #     elif "'NoneType' object has no attribute 'channel'" in str(error):
    #         await ctx.send("Such dir erstmal nen Audiokanal, du Otto")



    # @commands.command(help="SEID IHR BEREIT KINDER?")
    # async def Squad(self, ctx):
    #     squad_info = discord.Embed(title='MELDET EUCH ZUM DIENST!',description='BUBENSTATUS')
    #
    #     mongos_list = {"Peschko": "DiggaShishaBar", "Simon": "HiSim", "Felix": "Letax", "Johann": "Gammanus",
    #                    "Andrê": "Azzazzin", "Borenz": "SuiZiDaL28"}
    #     for x in mongos_list.keys():
    #         y = mongos_list[x]
    #         data = Bruder(name=y)
    #         print(data)
    #         if data[1] == "Ingame":
    #             playerinfo = "ist in einem {} mit {} seit {} auf dem Account {}".format(data[2],data[3],data[4].split(" ")[1],data[0])
    #         else:
    #             playerinfo = "ist nicht ingame"
    #         squad_info.add_field(name=str(x), value=playerinfo, inline=False)
    #
    #
    #     await ctx.send('', embed=squad_info)

    @commands.command(help="keckige witze")
    async def Wissen(self, ctx):
        await ctx.send(Mainbot())

class Magie(commands.Cog):
    """
    Weniger sinnlos, trotzdem Scheiße
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="mp3 Statistiken")
    async def mp3stats(self, ctx, *args):
        if len(args) == 0:
            mp3_list = []
            with open('res/mp3s_stats.txt', 'r', encoding='utf-8') as f:
                data = json.load(f)
            for x in data:
                mp3_list.append(x)
            res = Counter([x['Audiofile'] for x in mp3_list])
            z = dict(res)
            sortedRes = ({k: v for k, v in sorted(z.items(), key=lambda item: item[1], reverse=True)})
            dinv = {}
            for k, v in sortedRes.items():
                if v in dinv:
                    dinv[v].append(k)
                else:
                    dinv[v] = [k]
            dinv2 = str(dinv).replace("],","\n")
            mp3statsoutput = "".join(list(filter(lambda ch: ch not in "{}[]'", str(dinv2))))

            print("MP3Stats von {} angef ordert".format(ctx.author))
            with open("temp_mp3stats.txt","w") as tempfile:
                tempfile.write(mp3statsoutput)
            await ctx.send(file=discord.File(r'temp_mp3stats.txt'))
        elif len(args) == 1 and args[0] == "alt":
            with open('res/mp3s_stats.txt', 'r', encoding='utf-8') as g:
                data = json.load(g)
                namelist = []

                for x in data:
                    namelist.append(x["Audiofile"])

                itemset = set(namelist)
                itemdict = {}

                for x in itemset:
                    itemdict[x] = []

                for x in data:
                    if x["Audiofile"] in itemdict.keys():
                        itemdict[x["Audiofile"]].append(x["Zeit"])

                olddate_dict = {}
                for x in itemdict:
                    olddate_dict[x] = max(itemdict[x])

            mp3stats_alt = {k: v for k, v in sorted(olddate_dict.items(), key=lambda item: item[1])}

            mp3stats_alt = str(mp3stats_alt).replace(", ", "\n")

            with open("temp_mp3stats_alt.txt","w") as tempfile:
                tempfile.write(str(mp3stats_alt))
            await ctx.send(file=discord.File(r'temp_mp3stats_alt.txt'))

            try:
                os.remove("temp_mp3stats_alt.txt")
            except:
                print("temp_mp3stats_alt konnte nicht gelöscht werden")

        elif len(args) == 1 and args[0] == "alle":
            await ctx.send(file=discord.File(r'res/mp3s_stats.txt'))

    @commands.command(help="Unbenutze MP3s")
    async def unusedMP3(self, ctx):
        audiofiles_dropbox = []
        dropbox_filescan = dbx.files_list_folder("/discordbotmp3s")
        for x in dropbox_filescan.entries:
            audiofiles_dropbox.append(x.name)
        #print(audiofiles_dropbox)
        unusedmp3list = []
        with open('res/mp3s_stats.txt', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for x in audiofiles_dropbox:
                if str(x).replace(".mp3","") not in str(data):
                    unusedmp3list.append(x)

        await ctx.send("Unbenutzte mp3s:" + str(unusedmp3list).replace("[","").replace("]",""))

    @commands.command(help="Lösche von mp3stats")
    async def deleteFromMP3Stats(self, ctx, file):
        with open('res/mp3s_stats.txt', 'r+', encoding="utf-8") as e:
            data = json.load(e)
            newdata = list(data)
            for x in data:
                if file in x["Audiofile"]:
                    print(x)
                    newdata.remove(x)
            e.seek(0)
            e.truncate()
            jsondata = json.dumps(newdata)
            e.write(str(jsondata))
        try:
            os.remove('res/mp3s/{}.mp3'.format(file))
            dbx.files_delete_v2("/DiscordBotMp3s/{}.mp3".format(file))
        except:
            pass
        await ctx.send("Datei aus mp3stats gelöscht")
        await uploadMP3stats()

    @commands.command(help="MP3s die nicht mehr existieren")
    async def obsoleteMp3stat(self, ctx):
        with open('res/mp3s_stats.txt', 'r+', encoding="utf-8") as e:
            data = list(json.load(e))
            files = os.listdir('res/mp3s/')
            print(files)
            for x in data:
                if str(x["Audiofile"] + ".mp3") not in files:
                    await ctx.send(f"Datei {x['Audiofile']} aus MP3Stats gibt es nicht!")

    # @commands.command(help="Testcommand")
    # async def showString(self, ctx):
    #     print(ctx.message)


    @commands.command(help="Zeigt alle mp3s an")
    async def mp3s(self, ctx):
        files = os.listdir('res/mp3s/')
        files.sort()
        audiofiles = []
        for x in files:
            if ('.mp3' or '.wav') in str(x):
                audiofiles.append(x)
        print(len(str(audiofiles)))
        audiofiles.sort()
        if len(str(audiofiles)) > 2000:
            print("MP3Stats von {} angefordert".format(ctx.author))
            templist = []
            for x in audiofiles:
                templist.append(x)
                if len(templist) % 25 == 0:
                    print("test")
                    templist.sort()
                    await ctx.send(templist)
                    templist = []
            templist.sort()
            await ctx.send(templist)
        else:
            print(sorted(audiofiles))
            await ctx.send(sorted(audiofiles))

    @commands.command(help="löscht audiodatei")
    async def Delete(self, ctx, name):
        try:
            os.remove('res/mp3s/{}.mp3'.format(name))
            print(str(name) + " wurde vom lokalen System gelöscht")
        except Exception as e:
            print(e)
        dbx.files_delete_v2("/DiscordBotMp3s/{}.mp3".format(name))

        try:
            await Magie.deleteFromMP3Stats(ctx=ctx, file=name)
            await ctx.send(f"{name} wurde gelöscht und aus stats entfernt")
        except:
            await ctx.send("{} wurde gelöscht".format(name))



    @commands.command(help="löscht letzte x Nachrichten im Kanal")
    async def Genozid(self, ctx, limit: int):
        await ctx.channel.purge(limit=limit)
        await ctx.send('Cleared by {}'.format(ctx.author.mention))
        await ctx.message.delete()

    @commands.command(help="Zeigt Deutsche Arbeitszeit des Doktors")
    async def Aufzeit(self, ctx):
        endTime = datetime.now()
        print(endTime)
        await ctx.send('Ich bin schon {} stationiert'.format(endTime - startTime))

    @commands.command(help="URL der Audiodatei (mp3) anhängen + Name des Outputs")
    async def add_audiofile(self, ctx, link, name=None):
        print(link)
        if name == None:
            urllib.request.urlretrieve(link, "res/mp3s/"+str(link.split("/")[-1]))
        else:
            urllib.request.urlretrieve(link, "res/mp3s/" + str(name) + ".mp3")
        await ctx.send("Audiodatei " + str(link.split("/")[-1]) + " hinzugefügt")

    @commands.command(help="URL + Name + Startsekunde + Endsekunde")
    async def add_youtubeaudio(self, ctx=None, url=None, name=None, start=None, end=None, temp=None):

        print(f"Befehl [add_youtubeaudio] wird ausgeführt mit variablen {ctx}, {url}, {name}, {start}, {end}, {temp}")

        #command = f'youtube-dl.exe {url} -f 140 --audio-format "mp3" --output "test.mp3"'

        ydl_opts = {
            'outtmpl': 'test.mp3',
            'format': 'bestaudio/best',
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                #os.system(command)
                ydl.download([url])
                if start and end:
                    print("Youtubevideo runtergeladen von:" + str(ctx.author) + "[" + str(name) + " " + str(start) + " " + str(end) + "]")
                    if environment == "local":
                        ext = AudioClipExtractor('test.mp3', ffmpegpath)
                    elif environment == "heroku":
                        ext = AudioClipExtractor('test.mp3', 'vendor/ffmpeg/ffmpeg')

                    specs = str(start) + " " + str(end)
                    ext.extract_clips(specs)
                    try:
                        os.remove('res/mp3s/' + str(name).lower() + '.mp3')
                    except:
                        pass
                    print("renaming clip1 to proper filename")
                    os.rename('clip1.mp3', 'res/mp3s/' + str(name).lower() + '.mp3')
                    os.remove('test.mp3')
                else:
                    print("Youtubevideo runtergeladen von: " + str(ctx.author) + "[" + str(name) + "]")
                    os.rename('test.mp3', 'res/mp3s/' + str(name).lower() + '.mp3')
                if not temp:
                    await ctx.send("YT Video " + str(url) + " runtergeladen unter dem Namen: " + str(name))
            except Exception as e:
                await ctx.send("Es ist ein: " + str(e.__class__) + " Fehler aufgetreten.")
        if not temp:
            filestate = (dropbox_upload(name))
            print(filestate)
            if filestate == "upload_same":
                await ctx.send("Datei existiert bereits in anderer Länge. Überschreibe auf DropBox.")
            elif filestate == "upload":
                await ctx.send("Datei wurde nach DropBox hochgeladen")
            elif filestate == "overwrite":
                await ctx.send("Datei existiert bereits in anderer Länge. Überschreibe auf DropBox.")

    @commands.command(help="Alter Name + Neuer Name")
    async def Rename(self, ctx, oldfilevar, newfilevar):
        oldfile = oldfilevar.lower()
        newfile = newfilevar.lower()
        with open('res/mp3s_stats.txt', 'r+', encoding="utf-8") as e:
            data = e.read()
            print(data)
            if oldfile in data:
                print("test")
            newdata = data.replace('"Audiofile": "{}"'.format(oldfile), '"Audiofile": "{}"'.format(newfile))
            e.seek(0)
            e.write(newdata)
            await uploadMP3stats()
            print("Datei wurde in mp3stats umbenannt...")
        os.rename('res/mp3s/{}.mp3'.format(oldfile), 'res/mp3s/{}.mp3'.format(newfile))

        with open('res/mp3s/{}.mp3'.format(newfile), 'rb') as f:
            dbx.files_delete_v2("/DiscordBotMp3s/{}.mp3".format(oldfile))
            dbx.files_upload(f.read(), "/DiscordBotMp3s/{}.mp3".format(newfile))
        await ctx.send("Datei umbenannt")

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.id == 262510619503230976: #Shitheads
            for channel in guild.channels:
                if channel.name == "general":
                    #await channel.send("Bin gelandet auf Aldebaran.")
                    pass
        if guild.id == 733248970771660822: #Bot Test
            for channel in guild.channels:
                if channel.name == "general":
                    await channel.send("Bin gelandet auf Aldebaran.")

    dropbox_download()

    for guild in bot.guilds:
        if guild.id == 262510619503230976: #Shitheads
            for channel in guild.channels:
                if channel.name == "general":
                    #await channel.send("mp3 Dateien wurden von Dropbox runtergeladen.")
                    pass
        if guild.id == 733248970771660822: #Bot Test
            for channel in guild.channels:
                if channel.name == "general":
                    await channel.send("mp3 Dateien wurden von Dropbox runtergeladen.")

    print(f'{bot.user.name} has connected to {guild}')
    sys.stdout.flush()
    try:
        with open("res/mp3s_stats.txt", "wb") as h:
            metadata, res = dbx.files_download(path="/mp3s_stats.txt")
            h.write(res.content)

        print("mp3s_stats.txt runtergeladen")
    except:
        print("Datei existiert in DropBox nicht")

@bot.command()
async def leave(ctx):
        for x in bot.voice_clients:
            if(x.guild == ctx.message.guild):
                await x.disconnect(force=True)

@bot.command()
async def ytdlverbose(ctx, url):
    from subprocess import PIPE, run
    result = run('youtube-dl -v {}'.format(url), stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    x = result.stdout.split("\n")
    for y in x:
        if y:
            await ctx.send(y)


@bot.command()
async def uploadMP3stats(ctx=None):
    with open('res/mp3s_stats.txt', 'rb') as g:
        try:
            dbx.files_delete_v2("/mp3s_stats.txt")
        except:
            pass
        dbx.files_upload(g.read(), "/mp3s_stats.txt")
        if ctx:
            await ctx.send("MP3stats auf Dropbox hochgeladen")
        print("MP3stats auf Dropbox hochgeladen")


@bot.command()
async def downloadMP3stats(ctx):
    try:
        with open("res/mp3s_stats.txt", "wb") as h:
            metadata, res = dbx.files_download(path="/mp3s_stats.txt")
            h.write(res.content)
        await ctx.send("MP3stats von Dropbox runtergeladen")
        print("mp3s_stats.txt runtergeladen")
    except:
        print("Datei existiert in DropBox nicht")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "mama mia" in str(message.content).lower():
        await message.channel.send(file=discord.File('res/mamamia.png'))
    await bot.process_commands(message)
    if "donger" in str(message.content).lower():
        await message.channel.send("ヽ༼ຈل͜ຈ༽ﾉ")



bot.add_cog(Physik(bot))
bot.add_cog(Magie(bot))
bot.run(TOKEN)
