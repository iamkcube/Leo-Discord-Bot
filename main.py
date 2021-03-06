import discord
from webserver import keep_alive
import random
import asyncio
from discord.ext import commands
import re
import requests
import os
import youtube_dl
import time


def ytfirsturlreturn(query):

	results = requests.get(f'https://www.youtube.com/results?search_query={query.replace(" ","+")}').text
	found = re.findall(r'{"videoId":"[-.\d\w]+', results)[0].split("\"")[3]
	return f'https://youtu.be/{found}'

def yttitlereturn(url):
	results = requests.get(url).text[120000:300000]
	yttitle = re.findall(r'<title>[\w\W]+</title>', results)[0].replace(" - YouTube","").replace("&amp;","&").replace("<title>","").replace("</title>","")

	return yttitle

def soundcloudlinkreturn(song):
	searchresultlink = f'https://soundcloud.com/search?q={song.replace(" ","%20")}'

	searchresults = requests.get(searchresultlink).text

	limk = re.findall(r'<li><h2><a href="[a-zA-Z0-9/-]+', searchresults)[0].split('"')[1]

	return f'https://soundcloud.com{limk}'




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

intents = discord.Intents.all()

help_command = commands.DefaultHelpCommand(no_category = 'All Commands:')

myleo = commands.Bot(command_prefix="-",help_command = help_command , activity=discord.Activity(type=discord.ActivityType.listening, name="Music With You! ????"), intents = intents )

myleo.remove_command("help")


# HELP COMMAND
# --------------------------------------------------------------------------------------------------------


@myleo.group(invoke_without_command=True)
async def help(ctx):
	embed = discord.Embed(title="help" , description="Use -help <command> for more info on a command." , color=discord.Colour.teal())

	print(ctx.message.author.color)

	embed.add_field(name="help", value = "Shows this Message")
	embed.add_field(name="cls", value = "Clears only bots messages.")
	embed.add_field(name="fullqueue", value = "Shows the Whole Queue.")
	embed.add_field(name="join", value = "Joins the voice channel.")
	embed.add_field(name="leave", value = "Leaves the Voice Channel.")
	embed.add_field(name="next", value = "Skips to the next song in queue, else stops.")
	embed.add_field(name="loop", value = "This command toggles loop mode.")
	embed.add_field(name="nowplaying", value = "Now Playing!")
	embed.add_field(name="pause", value = "Pauses the Song.")
	embed.add_field(name="play", value = "Plays the songs and add to queue.")
	embed.add_field(name="queue", value = "Shows the queue.")
	embed.add_field(name="queueloop", value = "This command toggles queue loop mode")
	embed.add_field(name="remove", value = "Removes a song from the queue.")
	embed.add_field(name="replayqueue", value = "Replay the Full queue again.")
	embed.add_field(name="resume", value = "Resumes the Song.")
	embed.add_field(name="soundcloud", value = "soundcloud")
	embed.add_field(name="spotify", value = "Spotify Playlist")
	embed.add_field(name="stop", value = "Stops the Music Playback.")
	embed.add_field(name="ytplaylist", value = "Youtube Playlist")

	await ctx.send(embed=embed)


@help.command()
async def cls(ctx):
	embed = discord.Embed(title="Clears", description = "Clears only bots messages. (max. 100)" , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-cls [number of messages]", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def fullqueue(ctx):
	embed = discord.Embed(title="Full Queue", description = "Shows the Whole Queue. (with pagination)" , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-fullqueue")

	embed.add_field(name="**Aliases**", value= "allq , fullq , allqueue , allsongs , fq , aq", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def join(ctx):
	embed = discord.Embed(title="join", description = "Joins the voice channel." , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-join [best (*optional*)]")

	embed.add_field(name="**Aliases**", value= "j", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def leave(ctx):
	embed = discord.Embed(title="leave", description = "Leaves the Voice Channel" , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-leave")

	embed.add_field(name="**Aliases**", value= "l , dc , disconnect , bye , byeee , byeeee , bubyee , bubyeee", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def next(ctx):
	embed = discord.Embed(title="next", description = "Skips to the next song in queue, else stops." , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-next")

	embed.add_field(name="**Aliases**", value= "n , skip", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def nowplaying(ctx):
	embed = discord.Embed(title="nowplaying", description = "Now playing!" , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-nowplaying")

	embed.add_field(name="**Aliases**", value= "np", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def pause(ctx):
	embed = discord.Embed(title="pause", description = "Pauses the Song." , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-pause")

	embed.add_field(name="**Aliases**", value= "ps", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def play(ctx):
	embed = discord.Embed(title="play", description = "Plays the songs and add to queue" , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-play [name of song]")

	embed.add_field(name="**Aliases**", value= "p", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def queue(ctx):
	embed = discord.Embed(title="queue", description = "Shows the queue" , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-queue")

	embed.add_field(name="**Aliases**", value= "q", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def queueloop(ctx):
	embed = discord.Embed(title="queueloop", description = "This command toggles queue loop mode." , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-queueloop")

	embed.add_field(name="**Aliases**", value= "qloop , loopq , loopqueue", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def remove(ctx):
	embed = discord.Embed(title="remove", description = "Removes a song from the queue." , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-remove [queue number of song]")

	embed.add_field(name="**Aliases**", value= "rm", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def replayqueue(ctx):
	embed = discord.Embed(title="replayqueue", description = "Replay the Full queue again." , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-replayqueue")

	embed.add_field(name="**Aliases**", value= "rq", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def resume(ctx):
	embed = discord.Embed(title="resume", description = "Resumes the Song." , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-resume")

	embed.add_field(name="**Aliases**", value= "r , rs", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def soundcloud(ctx):
	embed = discord.Embed(title="soundcloud", description = "Soundcloud" , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-soundcloud [name of song]")

	embed.add_field(name="**Aliases**", value= "sc", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def spotify(ctx):
	embed = discord.Embed(title="spotify", description = "Spotify Playlist" , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-spotify [link of spotify playlist]")

	embed.add_field(name="**Aliases**", value= "spfy", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def stop(ctx):
	embed = discord.Embed(title="stop", description = "Stops the Music Playback." , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-stop")

	embed.add_field(name="**Aliases**", value= "st", inline=False)


	await ctx.send(embed=embed)


@help.command()
async def ytplaylist(ctx):
	embed = discord.Embed(title="ytplaylist", description = "Youtube Playlist" , color=ctx.message.author.color)

	embed.add_field(name="**Syntax**", value= "-ytplaylist [link]")

	embed.add_field(name="**Aliases**", value= "ytpl", inline=False)


	await ctx.send(embed=embed)



# MUSIC RELATED
# --------------------------------------------------------------------------------------------------------


myqueue=[]
allqueue=[]
nowplaying = ""
nowplayingurl = ""
loop = True



@myleo.event
async def on_ready():
	print('\nLeo is online!\n')
	print(os.getpid(),"\n")


@myleo.event
async def on_member_join(member):
	print("Hemlo!")
	for channel in member.guild.channels:
		if str(channel) == "answersheet" or str(channel)=="testing":
			print("greeting semt.")

			embed1 = discord.Embed(title=f"Welcome to {member.guild.name}", description=f"\nTama full/real name kuha tike. Bina pehchan admin rights diya habani.\n\n???", colour=discord.Colour.blue())
			try:
				print(str(member.avatar_url))
				embed1.set_image(url="https://c.tenor.com/fAIeksYoX3sAAAAd/aaiye-aapka-intezaar-tha-aaiye.gif")
				embed1.set_author(name=member.name,icon_url=str(member.avatar_url))
			except Exception as e:
				embed1.description=f"\n{member.mention}\nTama full/real name kuha tike. Bina pehchan admin rights diya habani.\n\n???"
			embed1.set_footer(text = "Aaiye Aapka Intezaar Tha XD")


			embed2 = discord.Embed(title=f"Welcome to {member.guild.name}", description=f"\nTama full/real name kuha tike. Bina pehchan admin rights diya habani.\n\n???", colour=discord.Colour.blue())
			try:
				print(str(member.avatar_url))
				embed2.set_image(url="https://c.tenor.com/K50rQKHNLD4AAAAC/tmkoc-dayabhabhi.gif")
				embed2.set_author(name=member.name,icon_url=str(member.avatar_url))
			except Exception as e:
				embed2.description=f"\n{member.mention}\nTama full/real name kuha tike. Bina pehchan admin rights diya habani.\n\n???"
			embed2.set_footer(text = "Aiiye Padhariye ????")


			embed3 = discord.Embed(title=f"Welcome to {member.guild.name}", description=f"\nTama full/real name kuha tike. Bina pehchan admin rights diya habani.\n\n???", colour=discord.Colour.blue())
			try:
				print(str(member.avatar_url))
				embed3.set_image(url=random.choice(["https://c.tenor.com/T0wtlyfEp8wAAAAC/sabbir31x-kaun-hai-be.gif","https://c.tenor.com/NQRZSwpZ6ZAAAAAC/pikachu-ara-bhay-par-tu-ha-kon.gif"]))
				embed3.set_author(name=member.name,icon_url=str(member.avatar_url))
			except Exception as e:
				embed3.description=f"\n{member.mention}\nTama full/real name kuha tike. Bina pehchan admin rights diya habani.\n\n???"
			embed3.set_footer(text = "Enjoy Here. ????")

			

			await channel.send(embed=random.choice([embed1,embed2,embed3]))



async def spotifyplaylist(ctx,limk,start,end):
	print("spotifyplaylist!\n")
	global myqueue

	songlistfinal = []
	
	playlist = requests.get(f'{limk}'.replace(" ","")).text[10000:20000]

	try:
		songlink1 = re.findall(fr'[-:/.\d\w]+" /><meta property="music:song:track" content="{start}"' , playlist)[0].split('"')[0]

		songsource1 = requests.get(songlink1).text 

		songname1 = re.findall(r'8"><title>[-. \d\w]+' , songsource1)[0].split('>')[2]

		await play(ctx,songname1)

	except Exception as e:
		print("Failed to get the song.\n")

		await ctx.send("Spotify is having some problems right now.")

		return



	for i in range(start,end):

		try:
			songlink = re.findall(fr'track" content="{i}" /><meta property="music:song" content="[-:/.\d\w]+' , playlist)[0].split('"')[6]

			songsource = requests.get(songlink).text 

			songname = re.findall(r'8"><title>[-. \d\w]+' , songsource)[0].split('>')[2]

			songlistfinal.append(ytfirsturlreturn(songname))

		except Exception as e:
			print("playlist ends here.\n")
			break

		time.sleep(2)

	print("\n",songlistfinal,"\n")
	myqueue.extend(songlistfinal)

	await ctx.send("Your Spotify Playlist has been added to the queue.")

	# await queue(ctx)



async def youtubeplaylist(ctx,limk,start,end):
	print("youtubeplaylist!\n")
	global myqueue

	ytsonglistfinal = []
	
	temxt = requests.get(limk.replace(" ","")).text

	try:
		creatorlis = re.findall(fr'"shortBylineText":{{"runs":[{{"text":"[a-zA-Z0-9,"|+\\/# ?]+', temxt)[0].replace("\u0026 more","").replace("\\u0026","")

		creator = creatorlis.split('"')[7]

		lis = re.findall(fr'[a-zA-Z0-9, ?]+"}}}}}},"index":{{"simpleText":"{start-1}"', temxt)[0]
		ytsongname1 = lis.split(f" by {creator}")[0]

		await play(ctx,ytsongname1)

	except Exception as e:
		print("Failed to get the song.\n")

		await ctx.send("Youtube is having some problems right now.")

		return



	for i in range(start,end):

		try:

			lis = re.findall(fr'[a-zA-Z0-9, ?]+"}}}}}},"index":{{"simpleText":"{i}"', temxt)[0]

			ytsongname = lis.split(f" by {creator}")[0]

			print(ytsongname , "\n")

			allqueue.append(ytsongname)

		except Exception as e:

			print("found all")
			break




	for i in range(start,end):
		try:
			hemlo = re.findall(fr'[a-zA-Z0-9,"_: ]+","index":{i},' , temxt)[0]

			vid_id = hemlo.split('"')[3]

			ytsonglistfinal.append(f'https://youtu.be/{vid_id}')

		except Exception as e:
			print("found all")
			break


	print("\n",ytsonglistfinal,"\n")

	myqueue.extend(ytsonglistfinal)

	await ctx.send("Your Youtube Playlist has been added to the queue.")



async def playsong(ctx,url):
	print("playsong!\n")
	global myqueue
	global nowplaying
	global nowplayingurl
	server = ctx.message.guild
	voice_channel = server.voice_client

	try:
		try:
			async with ctx.typing():
			   player = await YTDLSource.from_url(url, loop=myleo.loop)
			   voice_channel.play(player, after=lambda error: myleo.loop.create_task(check_queue(ctx)))
			   nowplaying = player.title
			   nowplayingurl = url
			await ctx.send(f'**Now playing:** {nowplaying}')
			print("Downloading.\n")
		except Exception as e:
			print("Streaming.\n")
			async with ctx.typing():
			   player = await YTDLSource.from_url(url, loop=myleo.loop , stream=True)
			   voice_channel.play(player, after=lambda error: myleo.loop.create_task(check_queue(ctx)))
			await ctx.send(f'**Now playing:** {player.title}')

	except Exception as e:
		await playsong(ctx,soundcloudlinkreturn(yttitlereturn(url)))

async def check_queue(ctx):
	print("check_queue!\n")
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
@commands.has_permissions(administrator=True)
async def clearmine(ctx,number=10):
	await ctx.channel.purge(limit=number+1)


@clearmine.error
async def clearmine_error(ctx,error):
	if isinstance(error,commands.CheckFailure):
		await ctx.send(f'{ctx.message.author.mention}, you need administrative rights first.')
		

@myleo.command(name='join',aliases=['j'],help="Joins the voice channel.")
async def join(ctx,*quality):
	print("Joined!\n")
	if not ctx.message.author.voice:
	   await ctx.send("You are not connected to a voice channel!")
	   return

	else:
	   channel = ctx.message.author.voice.channel

	try:
		await channel.connect(reconnect = True)
	except Exception as e:
		await channel.connect(reconnect = True)

	if quality != ():
		if "best" in quality[0].lower():
			ytdl_format_options['format'] = 'bestaudio/best'
			print("best music")
			await ctx.send("Best Quality Choosen.")
	else:
		ytdl_format_options['format'] = 'worstaudio/worst'


@myleo.command(name='loop', help='This command toggles loop mode')
async def loop(ctx):
	print("loop!\n")
	global loop

	if loop:
		await ctx.send('Loop mode is now on.')
		loop = True
	
	else:
		await ctx.send('Loop mode is now off')
		loop = False


@myleo.command(name='queueloop',aliases=['qloop', 'loopq', 'loopqueue' ] , help='This command toggles queue loop mode')
async def queueloop(ctx):
	print("queueloop!\n")
	global myqueue

	myqueue.extend(myqueue)
	await ctx.send('Looped the Queue.')




@myleo.command(name="play",aliases=['p'],help="Plays the songs and add to queue.")
async def play(ctx,*args):
	if ctx.voice_client == None:
		await join(ctx," ")

	print("play!\n")
	song = " ".join(args)
	global myqueue
	global allqueue

	server = ctx.message.guild
	voice_channel = server.voice_client

	if args[0].isnumeric():
		try:
			voice_channel.stop()
		except Exception as e:
			print("Couldn't stop music playback.")
			return
		finally:
			try:
				await playsong(ctx,myqueue[int(args[0])-1])
			except Exception as e:
				myqueue.extend([ytfirsturlreturn(song) for song in fullqueue])
				await playsong(ctx,myqueue[int(args[0])-1])

		
	else:
		try:
			url= ytfirsturlreturn(song)
		except Exception as e:
			return await ctx.send("Couldn't Find The Song. Sorry.")
		if voice_channel.source is not None:
			myqueue.append(url)
			queuedict[url] = yttitlereturn(url)
			return await ctx.send(f"I am currently playing a song, this song has been added to the queue at position: {len(myqueue)+1}.")


		try:
			print("\nusing yt.\n")
			await playsong(ctx,url)
			queuedict[url] = yttitlereturn(url)
		except Exception as e:
			print("\nusing soundcloud.\n")
			await playsong(ctx,soundcloudlinkreturn(song))
		allqueue.append(yttitlereturn(url))






@myleo.command(name="next",aliases=['n','skip'],help="Skips to the next song in queue, else stops.")
async def next(ctx):
	print("next!\n")
	ctx.voice_client.stop()

i=0
@myleo.command(name="leave",aliases=['l','dc','disconnect','bye','byeee','byeeee','bubyee','bubyeee'],help="Leaves the Voice Channel")
async def leave(ctx):
	print("left!\n")
	global i
	server = ctx.message.guild
	voice_channel = server.voice_client



	if voice_channel is not None:
		await voice_channel.disconnect()
		await ctx.send("Disconnected.")
	else:
		await join(ctx)
		if i>=1:
			i=0
			return
		i=i+1
		await leave(ctx)


@myleo.command(name='remove',aliases=['rm'], help='Removes a song from the queue.')
async def remove(ctx, number):
	print("removed!\n")
	global myqueue

	try:
		await ctx.send(f'Removed `{yttitlereturn(ytfirsturlreturn(myqueue[int(number)-1]))}`')
		del(myqueue[int(number)-1])
	
	except:
		await ctx.send('Your queue is either **empty** or the number is **out of range**.')


@myleo.command(name='queue',aliases=['q'], help='Shows the queue.')
async def queue(ctx):
	print("queue!\n")
	print(len(myqueue))
	if len(myqueue) == 0:
		await ctx.send("There are currently no songs in the queue.")

	else:
		async with ctx.typing():
			embed = discord.Embed(title="Song Queue", description="", colour=discord.Colour.blue())
			for i,url in enumerate(myqueue,1):
				yttitle = yttitlereturn(url)
				embed.description += f"{i}. {yttitle}\n"
				if yttitle not in allqueue:
					allqueue.append(yttitle)

			embed.set_footer(text="Keep Listening! <3")
			await ctx.send(embed=embed)


@myleo.command(name='fullqueue',aliases=['allq','fullq','allqueue','allsongs','fq','aq'], help='Shows the whole queue.')
async def fullqueue(ctx,*pagenum):
	print("fullqueue!\n")
	server = ctx.message.guild
	voice_channel = server.voice_client

	testnum = 1
	if pagenum != ():
		if pagenum[0].isnumeric():
			testnum = int(pagenum[0])

	print(testnum, " - testnum \n\nAllQueue\n")
	for i,song in enumerate(allqueue,1):
		print(f"{i}. {song}\n")

	if len(allqueue) == 0:
		await ctx.send("There are currently no songs in the queue.")

	else:
		embed = discord.Embed(title="Full Queue", description="", colour=discord.Colour.green())
		embed.description=""
		for i,song in enumerate(allqueue,1):
			if i<=15*(testnum-1):
				continue
			if i>15*(testnum):
				embed.description += "\n...and some more :sparkles:"
				break

			if nowplaying == song:
				embed.description += f"{i}. {song}\n:arrow_up:`now playing`\n"
			else:
				embed.description += f"{i}. {song}\n"

		embed.set_footer(text="Keep Listening! <3 \n(use -allq <page number> for next pages)")
		await ctx.send(embed=embed)



@myleo.command(name='replayqueue',aliases=['rq'],help='Replay the Full queue again.')
async def replayqueue(ctx,*args):
	global myqueue

	myqueue.extend([ ytfirsturlreturn(x) for x in allqueue ])

	await play(ctx,1)





@myleo.command(name='pause',aliases=['ps'],help='Pauses the Song.')
async def pause(ctx):
	print("pause!\n")
	server = ctx.message.guild
	voice_channel = server.voice_client
	if voice_channel.is_playing():
		voice_channel.pause()
		await ctx.send("Paused.")
	else:
		await ctx.send("No audio playing, but you're playing with your life, please pause that first.")


@myleo.command(name='resume',aliases=['r','rs'],help="Resumes the Song.")
async def resume(ctx):
	print("resume!\n")
	server = ctx.message.guild
	voice_channel = server.voice_client

	if voice_channel.is_paused():
		voice_channel.resume()
		await ctx.send("Resumed.")
	else:
		await ctx.send("Audio is already playing.")


@myleo.command(name='stop',aliases=['st'],help='Stops the Music Playback.')
async def stop(ctx):
	print("stop!\n")
	global myqueue
	server = ctx.message.guild
	voice_channel = server.voice_client

	voice_channel.stop()
	myqueue=[]
	await ctx.send("Stopped. Song Queue is Cleared.")


@myleo.command(name='spotify',aliases=['spfy'],help='Spotify Playlist')
async def spotify(ctx,*args):
	print("spotify!\n")
	limk = args[0]
	startendlist = args[1].split(",")
	# print(limk)
	async with ctx.typing():
		if len(startendlist)==2:
			await spotifyplaylist(ctx,str(limk),int(startendlist[0]),int(startendlist[1]))
		else:
			await spotifyplaylist(ctx,str(limk),1,11)



@myleo.command(name='ytplaylist',aliases=['ytpl'],help='Youtube Playlist')
async def ytplaylist(ctx,*args):
	print("ytplaylist!\n")
	limk = args[0]
	startendlist = args[1].split(",")
	async with ctx.typing():
		if len(startendlist)==2:
			await youtubeplaylist(ctx,str(limk),int(startendlist[0]),int(startendlist[1]))
		else:
			await youtubeplaylist(ctx,str(limk),1,11)



@myleo.command(name='soundcloud',aliases=['sc'],help='soundcloud')
async def soundcloud(ctx,*args):
	print("soundcloud!\n")
	print(args)
	song = " ".join(args)

	await playsong(ctx,soundcloudlinkreturn(song))

@myleo.command(name='nowplaying',aliases=['np'],help='Now Playing!')
async def nowplaying(ctx,*args):
	print("nowplaying!\n")
	print(nowplayingurl)

	embed = discord.Embed(title=nowplaying,description="**Now Playing**", url=nowplayingurl)

	await ctx.send(embed=embed)


@myleo.command(name='test',aliases=['testing'],help='test')
async def test(ctx,*args):
	print("test!\n")
	print(args)
	print(queuedict)
	limk = " ".join(args)
	await playsong(ctx,args[0])

@myleo.command(name='avatar',aliases=['av'],help='get your profile pic')
@commands.has_permissions(administrator=True)
async def avatar(ctx,*args):
	print("avatar!\n")
	print(args)
	print(queuedict)
	limk = " ".join(args)
	embed=discord.Embed(title=f"{ctx.message.author.name}'s Avatar",description=f'{ctx.message.author.mention}',colour=discord.Colour.red())
	embed.set_image(url=str(ctx.message.author.avatar_url))
	embed.set_footer(text="Yes, you can download it too.")
	await ctx.send(embed=embed)


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