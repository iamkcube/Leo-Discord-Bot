import discord
from webserver import keep_alive
import random
import asyncio
from discord.ext import commands
import re
import requests
import os
import youtube_dl
import pafy
import time
import random
from gtts import gTTS
from functools import lru_cache


def ytfirsturlreturn(query):
	results = requests.get(f'https://www.youtube.com/results?search_query={query.replace(" ","+")}').text
	found = re.findall(r'{"videoId":"[-.\d\w]+', results)[0].split("\"")[3]
	return f'https://youtu.be/{found}'

def gtexttospeech(text):
	mytext = str(text)
	language = 'hi'
	myobj = gTTS(text=mytext,lang=language,slow=False)
	myobj.save("talks.mp3")




# Ytdl Options 
# -------------------------------------------------------------------------------------------------------

ytdl_format_options = {
	# 'format': 'bestaudio/best',
	'format': 'worstaudio/worst',
	'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
	'restrictfilenames': True,
	'noplaylist': True,
	'nocheckcertificate': True,
	'ignoreerrors': False,
	'logtostderr': False,
	'quiet': True,
	'no_warnings': True,
	'default_search': 'auto',
	'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
	'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
	def __init__(self, source, *, data, volume=0.5):
		super().__init__(source, volume)

		self.data = data

		self.title = data.get('title')
		self.url = data.get('url')

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=False):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

		if 'entries' in data:
			# take first item from a playlist
			data = data['entries'][0]

		filename = data['url'] if stream else ytdl.prepare_filename(data)
		return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)



# Main Bot Code
# -------------------------------------------------------------------------------------------------------

help_command = commands.DefaultHelpCommand(no_category = 'All Commands:')

myleo = commands.Bot(command_prefix="-",help_command = help_command)



# MUSIC RELATED
# --------------------------------------------------------------------------------------------------------


myqueue=[]

allqueue=[]

loop = True


@myleo.event
async def on_ready():
	await myleo.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you from Heaven! <3"))
	print('Leo is online!')
	# await channel.send('Hey, It\'s me. Leo.') 
	print(os.getpid())



@lru_cache
async def spotifyplaylist(ctx,limk):
	global myqueue

	songlistfinal = []
	
	playlist = requests.get(f'{limk}&nd=1'.replace(" ","")).text

	songlink1 = re.findall(fr'[-:/.\d\w]+" /><meta property="music:song:track" content="1"' , playlist)[0].split('"')[0]

	songsource1 = requests.get(songlink1).text 

	songname1 = re.findall(r'8"><title>[-. \d\w]+' , songsource1)[0].split('>')[2]

	await play(ctx,songname1)


	for i in range(1,11):

		songlink = re.findall(fr'track" content="{i}" /><meta property="music:song" content="[-:/.\d\w]+' , playlist)[0].split('"')[6]

		songsource = requests.get(songlink).text 

		songname = re.findall(r'8"><title>[-. \d\w]+' , songsource)[0].split('>')[2]

		songlistfinal.append(ytfirsturlreturn(songname))
	print(songlistfinal)
	myqueue.extend(songlistfinal)


async def playsong(ctx,url):
	global myqueue
	server = ctx.message.guild
	voice_channel = server.voice_client

	try:
		async with ctx.typing():
		   player = await YTDLSource.from_url(url, loop=myleo.loop)
		   voice_channel.play(player, after=lambda error: myleo.loop.create_task(check_queue(ctx)))
		await ctx.send(f'**Now playing:** {player.title}')
		print("Downloading.")
	except Exception as e:
		async with ctx.typing():
		   player = await YTDLSource.from_url(url, loop=myleo.loop , stream=True)
		   voice_channel.play(player, after=lambda error: myleo.loop.create_task(check_queue(ctx)))
		await ctx.send(f'**Now playing:** {player.title}')
		print("Streaming.")


async def check_queue(ctx):
	if len(myqueue) > 0:
		await playsong(ctx, myqueue[0])
		if loop:
			myqueue.pop(0)
	else:
		server = ctx.message.guild
		voice_channel = server.voice_client

		voice_channel.stop()


def is_me(m):
	return m.author == myleo.user



@myleo.command(name="cls",help="Clears only bots messages, number can be specified.")
async def cls(ctx,number=100):
	async for message in ctx.channel.history(limit=number):
		if is_me(message):
			await message.delete()


@myleo.command(name="clearmine",aliases=['clm'],help="Clears all messages to a range.")
async def clearmine(ctx,number=10):
	await ctx.channel.purge(limit=number+1)


@myleo.command(name='join',aliases=['j'],help="Joins the voice channel.")
async def join(ctx,*quality):

	if not ctx.message.author.voice:
	   await ctx.send("You are not connected to a voice channel!")
	   return

	else:
	   channel = ctx.message.author.voice.channel

	await channel.connect(reconnect = True)

	if quality != ():
		if "best" in quality[0].lower():
			ytdl_format_options['format'] = 'bestaudio/best'
			print("best music")
			await ctx.send("Best Quality Choosen.")
	else:
		ytdl_format_options['format'] = 'worstaudio/worst'


@myleo.command(name='loop', help='This command toggles loop mode')
async def loop_(ctx):
	global loop

	if loop:
		await ctx.send('Loop mode is now on.')
		loop = True
	
	else:
		await ctx.send('Loop mode is now off')
		loop = False




@myleo.command(name="play",aliases=['p'],help="Plays the songs and add to queue.")
async def play(ctx,*args):
	song = " ".join(args)
	global myqueue
	global allqueue

	server = ctx.message.guild
	voice_channel = server.voice_client

	if voice_channel.source is not None:
		myqueue.append(ytfirsturlreturn(song))
		allqueue.append(ytfirsturlreturn(song))
		return await ctx.send(f"I am currently playing a song, this song has been added to the queue at position: {len(myqueue)+1}.")


	await playsong(ctx,ytfirsturlreturn(song))




@myleo.command(name="next",aliases=['n','skip'],help="Skips to the next song in queue, else stops.")
async def next(ctx):
	ctx.voice_client.stop()

i=0
@myleo.command(name="leave",aliases=['l','dc','disconnect','bye','byeee','byeeee','bubyee','bubyeee'],help="Leaves the Voice Channel") #work needed to be done
async def leave(ctx):
	global i
	server = ctx.message.guild
	voice_channel = server.voice_client



	if voice_channel is not None:
		await voice_channel.disconnect()
		await ctx.send("Disconnected. Bubyee, Cutiepies.")
	else:
		await join(ctx)
		i=i+1
		if i>=1:
			i=0
			return
		await leave(ctx)


@myleo.command(name='remove',aliases=['rm'], help='Removes a song from the queue.')
async def remove(ctx, number):
	global myqueue

	try:
		await ctx.send(f'Removed `{pafy.new(ytfirsturlreturn(myqueue[int(number)-1])).title}`')
		del(myqueue[int(number)-1])
	
	except:
		await ctx.send('Your queue is either **empty** or the number is **out of range**.')


@lru_cache
@myleo.command(name='queue',aliases=['q'], help='Shows the queue.')
async def queue(ctx):
	if len(myqueue) == 0:
		await ctx.send("There are currently no songs in the queue.")

	else:
		embed = discord.Embed(title="Song Queue", description="", colour=discord.Colour.blue())
		for i,url in enumerate(myqueue,1):
			embed.description += f"{i}. {pafy.new(url).title}\n"

		embed.set_footer(text="Keep Listening! <3")
		await ctx.send(embed=embed)

@myleo.command(name='fullqueue',aliases=['allq'], help='Shows the whole queue.')
async def fullqueue(ctx):
	server = ctx.message.guild
	voice_channel = server.voice_client

	if len(allqueue) == 0:
		await ctx.send("There are currently no songs in the queue.")

	else:
		embed = discord.Embed(title="Full Queue", description="", colour=discord.Colour.blue())
		embed.description=""
		for i,url in enumerate(allqueue,1):
			if myqueue == [] and voice_channel.is_playing():
				embed.description += "\t`now playing`\n"
			elif url == myqueue[0]:
				embed.description += f"\t`now playing`\n{i}. {pafy.new(url).title}\n"
			else:
				embed.description += f"{i}. {pafy.new(url).title}\n"


		embed.set_footer(text="Keep Listening! <3")
		await ctx.send(embed=embed)


@myleo.command(name='pause',aliases=['ps'],help='Pauses the Song.')
async def pause(ctx):
	server = ctx.message.guild
	voice_channel = server.voice_client
	if voice_channel.is_playing():
		voice_channel.pause()
		await ctx.send("Paused.")
	else:
		await ctx.send("No audio playing, but you're playing with your life, please pause that first.")


@myleo.command(name='resume',aliases=['r','rs'],help="Resumes the Song.")
async def resume(ctx):
	server = ctx.message.guild
	voice_channel = server.voice_client

	if voice_channel.is_paused():
		voice_channel.resume()
		await ctx.send("Resumed.")
	else:
		await ctx.send("Audio is already playing.")


@myleo.command(name='stop',aliases=['st'],help='Stops the Music Playback.')
async def stop(ctx):
	global myqueue
	server = ctx.message.guild
	voice_channel = server.voice_client

	voice_channel.stop()
	myqueue=[]
	await ctx.send("Stopped. Song Queue is Cleared.")


@myleo.command(name='spotify',aliases=['spfy'],help='Spotify Playlist')
async def spotify(ctx,*args):
	limk = " ".join(args)
	# print(limk)
	await spotifyplaylist(ctx,str(limk))



@myleo.command(name='serverrestart',aliases=['srestart','restartserver'],help='Server Restart')
async def serverrestart(ctx):
	with open("restartleo.bat","w") as f:
		f.write(f'''@echo off
taskkill /pid {os.getpid()} /t /f
python main.py
cmd''')
		os.startfile("initiate.bat")




keep_alive()
my_secret = os.environ['Token']
myleo.run(my_secret)
# my_secret = os.environ['Token']
# myleo.run(my_secret)