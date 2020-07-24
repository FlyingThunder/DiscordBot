# DiscordBot
muss man WISSEN




Dependencies:

Python Libs: See requirements.txt

Discord Bot (obviously): https://discord.com/developers

Reddit API: https://www.reddit.com/prefs/apps

WHEN HOSTING LOCALLY:

add API keys to example.env and rename to .env

FFMPEG.exe in /res/: https://ffmpeg.zeranoe.com/builds/
adding `executable=ffmpegpath,` as an argument in ` vc.play(discord.FFmpegPCMAudio())`


WHEN HOSTING ON HEROKU, LIKE I AM:

add API keys to configvars
use procfile to tell heroku what the main script is
use runtime.txt to choose a python interpreter
add the following buildpacks:
`heroku/python`
`https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git`
`https://github.com/kitcast/buildpack-ffmpeg.git`
`https://github.com/xrisk/heroku-opus.git`
