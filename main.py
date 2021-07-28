import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import praw
import json
import sys
from datetime import datetime
import urllib.request
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


dbx = dropbox.Dropbox(dropbox_key)

environment = "heroku" #local/heroku

# bot command präfix
bot = commands.Bot(command_prefix='!', case_insensitive=True)
bot.remove_command("help")
ffmpegpath = "ffmpeg.exe"
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
        f.close()
        return "upload"
    else:
        if os.path.getsize('res/mp3s/{}'.format(x.lower())) != dbx.files_get_metadata("/discordbotmp3s/{}".format(x)).size:
            print("Datei vorhanden, Metadaten nicht identisch. Überschreibe auf DropBox.")
            f = open('res/mp3s/{}'.format(x.lower()), 'rb')
            dbx.files_delete_v2("/DiscordBotMp3s/{}".format(x))
            dbx.files_upload(f.read(), "/DiscordBotMp3s/{}".format(x))
            f.close()
            return "overwrite"
        else:
            f = open('res/mp3s/{}'.format(x.lower()), 'rb')
            dbx.files_delete_v2("/DiscordBotMp3s/{}".format(x))
            dbx.files_upload(f.read(), "/DiscordBotMp3s/{}".format(x))
            f.close()
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

async def Labern(audiofile, volume, ctx, tagged=None):
    print(f"Labern gestartet mit Datei: {audiofile}, Lautstärke: {volume}, ctx: {ctx}")
    def my_after(error):
        import asyncio
        coro = voice_client.disconnect()
        fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
        try:
            fut.result()
        except:
            pass
    try:
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice_client.is_connected():
           if ctx.voice_client.channel is not ctx.message.author.voice.channel:
               await ctx.voice_client.move_to(ctx.message.author.voice.channel)
    except:
        print("Exception in creating voice client:" + str(Exception))

    if volume is None:
        print(f"spiele audiofile {audiofile.lower()} ab")
        ctx.voice_client.play(discord.FFmpegPCMAudio('res/mp3s/{}.mp3'.format(audiofile.lower())),after=my_after)
        #ctx.voice_client.play(discord.FFmpegOpusAudio('res/mp3s/{}.mp3'.format(audiofile.lower()), bitrate=24, executable=ffmpeg, pipe=False),after=my_after)
    else:
        ctx.voice_client.play(discord.FFmpegPCMAudio('res/mp3s/{}.mp3'.format(audiofile.lower())),after=my_after)
        ctx.voice_client.source = discord.PCMVolumeTransformer(ctx.voice_client.source)
        ctx.voice_client.source.volume = float(volume)
        print(volume)


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
    async def Random(self, ctx, argument="1"):



        print(f"Random argument: '{argument}'")
        file = random.choice(os.listdir("res/mp3s/"))
        print(f"Zufallsdatei {file} ausgewählt")
        cutfile = file.replace(".mp3","")

        if argument == "random":
            volume = random.randint(0,50)
            print(f"Zufallslautstärke {str(volume)} ausgewählt")
        else:
            volume = int(argument)

        await Labern(audiofile=cutfile, volume=volume, ctx=ctx)

    @commands.command(help="Dateinahmen anhängen ODER url von Youtubevideo")
    async def Sag(self, ctx, argument=None, *args):
        url = None
        play = None

        args = list(args)

        print("ctx: " + str(ctx))
        print("played file/url: " + str(argument))
        print("args: " + str(args))

        for x in args:
            if "@" in str(x):
                index = args.index(x)
                del args[index]

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
                    await Labern(audiofile=play, volume=args[0], ctx=ctx)
                else:
                    await Labern(audiofile=play, volume=None, ctx=ctx)

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
                try:
                    print("Versuche temp_file.mp3 zu löschen")
                    os.remove('res/mp3s/temp_file.mp3')
                except:
                    print("Scheint nicht zu existieren?")
                if len(args) == 0: #ganzes video, ohne volume
                    await Magie.add_youtubeaudio(Magie(bot), url=url, ctx=ctx, name="temp_file", temp=True)
                    try:
                        print("Audiodatei wird abgespielt: " + "temp_file" + " von: " + str(ctx.author))
                        await Labern(audiofile="temp_file", ctx=ctx, volume=None)
                    except Exception as e:
                        await ctx.send("Spast" + " " + ctx.author.mention)
                        print("Exception:" + str(e))
                    print("Audiodatei wird aus Youtubevideo abgespielt und anschließend gelöscht: " + url + "von: " + str(ctx.author))
                if len(args) == 1: #ganzes video, mit volume
                    await Magie.add_youtubeaudio(Magie(bot), url=url, ctx=ctx, name="temp_file", temp=True)
                    try:
                        print("Audiodatei wird abgespielt: " + "temp_file" + " von: " + str(ctx.author))
                        await Labern(audiofile="temp_file", ctx=ctx, volume=args[0])
                    except Exception as e:
                        await ctx.send("Spast" + " " + ctx.author.mention)
                        print("Exception:" + str(e))
                    print("Audiodatei wird aus Youtubevideo abgespielt und anschließend gelöscht: " + url + "von: " + str(ctx.author))
                elif len(args) == 2: #start + end
                    await Magie.add_youtubeaudio(Magie(bot), url=url, ctx=ctx, name="temp_file", start=args[0], end=args[1], temp=True)
                    try:
                        print("Audiodatei wird abgespielt: " + "temp_file" + " von: " + str(ctx.author))
                        await Labern(audiofile="temp_file", ctx=ctx, volume=None)
                    except Exception as e:
                        await ctx.send("Spast" + " " + ctx.author.mention)
                        print("Exception:" + str(e))
                    print("Audiodatei wird aus Youtubevideo abgespielt und anschließend gelöscht: " + url + "Zeit: " + str(args[0]) + " / " + str(args[1]) +  " von: " + str(ctx.author))
                elif len(args) == 3: #start+end+volume
                    await Magie.add_youtubeaudio(Magie(bot), url=url, ctx=ctx, name="temp_file", start=args[0], end=args[1], temp=True)
                    try:
                        print("Audiodatei wird abgespielt: " + "temp_file" + " von: " + str(ctx.author))
                        await Labern(audiofile="temp_file", ctx=ctx, volume=args[2])
                    except Exception as e:
                        await ctx.send("Spast" + " " + ctx.author.mention)
                        print("Exception:" + str(e))
                    print("Audiodatei wird aus Youtubevideo abgespielt und anschließend gelöscht: " + url + "Zeit: " + str(args[0]) + " / " + str(args[1]) +  " von: " + str(ctx.author))

        else:
            await ctx.send("Dumm oder was?")

    @Sag.before_invoke
    @Random.before_invoke
    async def ensure_voice(self, ctx):
        print(ctx.message.content.split(" "))
        if "<@!" in str(ctx.message.content.split(" ")):
            print("User tagged someone - ignoring author voice channel check")
            getuser = ctx.message.mentions[0].voice.channel
            await getuser.connect()
        else:
            if ctx.voice_client is None:
                if ctx.author.voice:
                    await ctx.author.voice.channel.connect()
                else:
                    await ctx.send("You are not connected to a voice channel.")
                    raise commands.CommandError("Author not connected to a voice channel.")
            elif ctx.voice_client.is_playing():
                await ctx.voice_client.disconnect()


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
                        print("Trying to remove old file")
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
    await bot.process_commands(message)
    if "donger" in str(message.content).lower():
        await message.channel.send("ヽ༼ຈل͜ຈ༽ﾉ")



bot.add_cog(Physik(bot))
bot.add_cog(Magie(bot))
bot.run(TOKEN)
