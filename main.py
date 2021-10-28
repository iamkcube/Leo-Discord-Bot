import discord
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

poinnn = commands.Bot(command_prefix=".",help_command = help_command)


# TICTACTOE
# --------------------------------------------------------------------------------------------------------


player1 = ""
player2 = ""
turn = ""
gameOver = True

board = []

winningConditions = [
	[0, 1, 2],
	[3, 4, 5],
	[6, 7, 8],
	[0, 3, 6],
	[1, 4, 7],
	[2, 5, 8],
	[0, 4, 8],
	[2, 4, 6]
]

@poinnn.command(name='tictactoe',aliases=['ttt'],help='Starts the Game. Add player names.')
async def tictactoe(ctx, p1: discord.Member, p2: discord.Member):
	global count
	global player1
	global player2
	global turn
	global gameOver

	if gameOver:
		global board
		board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
				 ":white_large_square:", ":white_large_square:", ":white_large_square:",
				 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
		turn = ""
		gameOver = False
		count = 0

		player1 = p1
		player2 = p2

		# print the board
		line = ""
		for x in range(len(board)):
			if x == 2 or x == 5 or x == 8:
				line += " " + board[x]
				await ctx.send(line)
				line = ""
			else:
				line += " " + board[x]

		# determine who goes first
		num = random.randint(1, 2)
		if num == 1:
			turn = player1
			await ctx.send("It is <@" + str(player1.id) + ">'s turn.")
		elif num == 2:
			turn = player2
			await ctx.send("It is <@" + str(player2.id) + ">'s turn.")
	else:
		await ctx.send("A game is already in progress! Finish it before starting a new one.")

@poinnn.command(name="place",help="Places your Cross/Circle.")
async def place(ctx, pos: int):
	global turn
	global player1
	global player2
	global board
	global count
	global gameOver

	if not gameOver:
		mark = ""
		if turn == ctx.author:
			if turn == player1:
				mark = ":regional_indicator_x:"
			elif turn == player2:
				mark = ":o2:"
			if 0 < pos < 10 and board[pos - 1] == ":white_large_square:" :
				board[pos - 1] = mark
				count += 1

				# print the board
				line = ""
				for x in range(len(board)):
					if x == 2 or x == 5 or x == 8:
						line += " " + board[x]
						await ctx.send(line)
						line = ""
					else:
						line += " " + board[x]

				checkWinner(winningConditions, mark)
				print(count)
				if gameOver == True:
					await ctx.send(mark + " wins!")
				elif count >= 9:
					gameOver = True
					await ctx.send("It's a tie!")

				# switch turns
				if turn == player1:
					turn = player2
				elif turn == player2:
					turn = player1
			else:
				await ctx.send("Be sure to choose an integer between 1 and 9 (inclusive) and an unmarked tile.")
		else:
			await ctx.send("It is not your turn.")
	else:
		await ctx.send("Please start a new game using the !tictactoe command.")


def checkWinner(winningConditions, mark):
	global gameOver
	for condition in winningConditions:
		if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
			gameOver = True

@tictactoe.error
async def tictactoe_error(ctx, error):
	print(error)
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("Please mention 2 players for this command.")
	elif isinstance(error, commands.BadArgument):
		await ctx.send("Please make sure to mention/ping players (ie. <@688534433879556134>).")

@place.error
async def place_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send("Please enter a position you would like to mark.")
	elif isinstance(error, commands.BadArgument):
		await ctx.send("Please make sure to enter an integer.")






# RANDOM FUN EASTER EGGS
# --------------------------------------------------------------------------------------------------------

def playtalk(ctx,mylist):
	server = ctx.message.guild
	voice_channel = server.voice_client

	gtexttospeech(random.choice(mylist))
	time.sleep(1)
	voice_channel.play(discord.FFmpegPCMAudio("talks.mp3"))

@poinnn.command(name="hemlo",aliases=['Hemlo','hemlu','Hemlu','hello','Hello','hey','Hey','heyy','Heyy','hi','Hi','hii','Hii','hiii','Hiii'],help="Try it out yourself!")
async def hemlo(ctx,args):
	mess = " ".join(args).lower()
	if "poi" in mess or "poinnn" in mess:
		if ctx.message.author.nick is not None and ctx.message.author.nick != "Kkk":
			await ctx.send(f"Hemlo Cutiepie {ctx.message.author.nick}! Hope you\'re doing good. And you\'re the best.:heart:")
		else:
			await ctx.send(f'Hemlo {str(ctx.message.author).split("#")[0]}! Hope you\'re doing good. :heart:')

@poinnn.command(name="what",aliases=['What','whatt','Whatt','whaat','Whaat'],help="Try it out yourself!")
async def what(ctx,*args):
	mess = " ".join(args).lower()
	# print(args)
	if "doing" in mess:
		await ctx.send(f"Me is here to cheer you up!")
	if "do" in mess and "can" in mess:
		await ctx.send(f"Me is here to cheer you up!")

@poinnn.command(name="how",aliases=['How','howw','Howw','howww','Howww'],help="Try it out yourself!")
async def how(ctx,*args):
	mess = " ".join(args).lower()
	if "you" in mess or "u" in mess :
		await ctx.send(f'I\'m Good. How are you !? ')
	if str(ctx.message.author.nick).lower() == 'mamun':
		mamunchoice=['You look like a fairy :woman_fairy_tone1:','Why did you go to earth, Angel :woman_fairy_tone1:','The alphabet has 21 letters, because the others spell U, R, A, Q,T.(lol my bestie google helmped me)']
		if 'i' in mess and 'look' in mess:
			await ctx.send(random.choice(mamunchoice))

@poinnn.command(name="i",aliases=['I','im','Im','I\'m','i\'m'],help="Try it out yourself!")
async def i(ctx,*args):
	mess = " ".join(args).lower()
	if "fine" in mess or "okay" in mess or "good" in mess or "happy" in mess or "nice" in mess :
		await ctx.send("Stay Happy. I'm always there for you!")

@poinnn.command(name="love",aliases=['lobh','Lobh','lobhh','Lobhh','Lou','lou','Louu','louu'],help="Try it out yourself!")
async def love(ctx,*args):
	await ctx.send("https://tenor.com/view/guess-what-your-a-cutiepie-cat-gif-8499003")

@poinnn.command(name="lomdi",aliases=['Lomdi'],help="Try it out yourself!")
async def lomdi(ctx,*args):
	await ctx.send("No Fox Given.")

@poinnn.command(name="mistax",aliases=['mixtax','Mixtax','Mistax','Mixtaxx','Mistaxx','mixtaxx','mistaxx'],help="Try it out yourself!")
async def mistax(ctx,*args):
	await ctx.send("Happenx Somthim.")

@poinnn.command(aliases=['Aww','awww','Awww','awwww','Awwww','awwwww','Awwwww','awwwwww','Awwwwww'])
async def aww(ctx,*args):
	await ctx.send(f"Poin Lawwbhs You {ctx.message.author.nick}")

@poinnn.command(name="search", aliases=['s','Search','S'],help="Search Anything.")
async def search(ctx,*args):
	mess = " ".join(args).lower()
	if "mamun" in mess:
		mamunchoice = ["Where is You Mamun!? I miss you :pleading_face:","I shall go & find Mamun wherever she is. :pleading_face:","Finding Mamun real quick. :pleading_face:"]
		await ctx.send(random.choice(mamunchoice))

@poinnn.command(name="poin", aliases=['poi','Poi','Poin'],help="Talk to me.")
async def poin(ctx,*args):
	mess = " ".join(args).lower()
	if "mamun" in mess and 'look' in mess:
		mamunchoice = ["Where is You Mamun!? I miss you :pleading_face:","I shall go & find Mamun wherever she is. :pleading_face:","Finding Mamun real quick. :pleading_face:"]
		await ctx.send(random.choice(mamunchoice))

	if str(ctx.message.author.nick).lower() == 'mamun':
		mamunchoice=['You look like a fairy :woman_fairy_tone1:','Why did you go to earth, Angel :woman_fairy_tone1:','The alphabet has 21 letters, because the others spell U, R, A, Q,T.(lol my bestie google helmped me)']
		if 'how' in mess and 'i' in mess and 'look' in mess:
			await ctx.send(random.choice(mamunchoice))

	if "say" in mess:
		# English-----
		if "hello" in mess:
			mamunchoice=["Hemlo Lom diz","Hemlo guys! I'm good!"]
			playtalk(ctx,mamunchoice)

		# Hindi-------
		if "kya" in mess and "kar" in mess and "ho" in mess:
			mamunchoice=['Mast Biriyani khaa rahi hoon, Tum batao.','Ghumne jaa rahi hoon','Movie dekh rahi hoon','Ded in Bed. Yes, Happenx Ebherytim.']
			playtalk(ctx,mamunchoice)

@poinnn.command(name="say", aliases=['Say','speak','Speak','bol','Bol','Bolo','bolo','kaha',"Kaha",'kah','Kah'],help="Make me say!")
async def say(ctx,*args):
	mess = " ".join(args).lower()
	playtalk(ctx,[mess])










# MUSIC RELATED
# --------------------------------------------------------------------------------------------------------


myqueue=[]

allqueue=[]

loop = True


@poinnn.event
async def on_ready():
	await poinnn.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you from Heaven! <3"))
	print('Poin is online!')



async def playsong(ctx,url):
	global myqueue
	server = ctx.message.guild
	voice_channel = server.voice_client

	async with ctx.typing():
	   player = await YTDLSource.from_url(url, loop=poinnn.loop)
	   voice_channel.play(player, after=lambda error: poinnn.loop.create_task(check_queue(ctx)))
	await ctx.send(f'**Now playing:** {player.title}')

async def check_queue(ctx):
	if len(myqueue) > 0:
		await playsong(ctx, myqueue[0])
		if loop:
			myqueue.pop(0)

def is_me(m):
	return m.author == poinnn.user



@poinnn.command(name="cls",help="Clears only bots messages, number can be specified.")
async def cls(ctx,number=100):
	async for message in ctx.channel.history(limit=number):
		if is_me(message):
			await message.delete()


@poinnn.command(name="clearmine",aliases=['clm'],help="Clears all messages to a range.")
async def clearmine(ctx,number=10):
	await ctx.channel.purge(limit=number+1)


@poinnn.command(name='join',aliases=['j'],help="Joins the voice channel.")
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


@poinnn.command(name='loop', help='This command toggles loop mode')
async def loop_(ctx):
	global loop

	if loop:
		await ctx.send('Loop mode is now on.')
		loop = True
	
	else:
		await ctx.send('Loop mode is now off')
		loop = False




@poinnn.command(name="play",aliases=['p'],help="Plays the songs and add to queue.")
async def play(ctx,*,song):
	global myqueue
	global allqueue

	server = ctx.message.guild
	voice_channel = server.voice_client

	if voice_channel.source is not None:
		myqueue.append(ytfirsturlreturn(song))
		allqueue.append(ytfirsturlreturn(song))
		return await ctx.send(f"I am currently playing a song, this song has been added to the queue at position: {len(myqueue)+1}.")


	await playsong(ctx,ytfirsturlreturn(song))




@poinnn.command(name="next",aliases=['n','skip'],help="Skips to the next song in queue, else stops.")
async def next(ctx):
	ctx.voice_client.stop()


@poinnn.command(name="leave",aliases=['l','dc','disconnect','bye','byeee','byeeee','bubyee','bubyeee'],help="Leaves the Voice Channel") #work needed to be done
async def leave(ctx):
	server = ctx.message.guild
	voice_channel = server.voice_client

	if voice_channel is not None:
		await voice_channel.disconnect()
		await ctx.send("Disconnected. Bubyee, Cutiepies.")
	else:
		await join(ctx)
		await leave(ctx)


@poinnn.command(name='remove',aliases=['rm'], help='Removes a song from the queue.')
async def remove(ctx, number):
	global myqueue

	try:
		del(myqueue[int(number)-1])
		await ctx.send(f'Removed `{pafy.new(ytfirsturlreturn(myqueue[int(number)-1])).title}`')
	
	except:
		await ctx.send('Your queue is either **empty** or the number is **out of range**.')


@poinnn.command(name='queue',aliases=['q'], help='Shows the queue.')
async def queue(ctx):
	if len(myqueue) == 0:
		await ctx.send("There are currently no songs in the queue.")

	else:
		embed = discord.Embed(title="Song Queue", description="", colour=discord.Colour.blue())
		for i,url in enumerate(myqueue,1):
			embed.description += f"{i}. {pafy.new(url).title}\n"

		embed.set_footer(text="Keep Listening! <3")
		await ctx.send(embed=embed)

@poinnn.command(name='fullqueue',aliases=['allq'], help='Shows the whole queue.')
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


@poinnn.command(name='pause',aliases=['ps'],help='Pauses the Song.')
async def pause(ctx):
	server = ctx.message.guild
	voice_channel = server.voice_client
	if voice_channel.is_playing():
		voice_channel.pause()
		await ctx.send("Paused.")
	else:
		await ctx.send("No audio playing, but you're playing with your life, please pause that first.")


@poinnn.command(name='resume',aliases=['r','rs'],help="Resumes the Song.")
async def resume(ctx):
	server = ctx.message.guild
	voice_channel = server.voice_client

	if voice_channel.is_paused():
		voice_channel.resume()
		await ctx.send("Resumed.")
	else:
		await ctx.send("Audio is already playing.")


@poinnn.command(name='stop',aliases=['st'],help='Stops the Music Playback.')
async def stop(ctx):
	global myqueue
	server = ctx.message.guild
	voice_channel = server.voice_client

	voice_channel.stop()
	myqueue=[]
	await ctx.send("Stopped. Song Queue is Cleared.")


Token="ODk0OTg3MzE4ODc4OTQ5NDI5.YVx_5A.SmWGf_dvXrVQ8yGlFgZy6erXz9A" ; poinnn.run(Token)
# my_secret = os.environ['Token']
# poinnn.run(my_secret)