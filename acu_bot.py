import discord
import youtube_dl
import asyncio

from discord.ext import commands

# Set the command prefix
client = commands.Bot(command_prefix='m.')

# Set the token for the Discord bot
TOKEN = 'MTA0OTMxODQwNzkzOTU3MTc5Mw.G7AzRp.Da85wbEPxrh7-JGxZnsf3YQqVpJLfoqXqMW6R'

# Dictionary to store the playlist
playlist = {}

# Dictionary to store the state of the music player
players = {}


# Play a song in the voice channel
async def play(ctx, url):
    server = ctx.message.guild
    voice_channel = server.voice_client

    # Check if the bot is already playing music
    if server.id in players:
        if players[server.id].is_playing():
            await ctx.send('Music is already playing.')
            return

    # Set up the music player
    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'default_search': 'auto'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)

    player = voice_channel.play(source)

    # Store the music player in the dictionary
    players[server.id] = player

    # Wait for the song to end
    await asyncio.sleep(info['duration'])

    # Remove the song from the playlist
    playlist[server.id].pop(0)

    # Check if there are any songs left in the playlist
    if len(playlist[server.id]) > 0:
        # Play the next song in the playlist
        await play(ctx, playlist[server.id][0]['url'])
    else:
        # Disconnect from the voice channel
        await voice_channel.disconnect()


# Define the bot commands
@client.command()
async def Hi(ctx):
    await ctx.send('meow')

@client.command()
async def hi(ctx):
    await ctx.send('meow')

@client.command()
async def clean(ctx, amount=1):
    await ctx.channel.purge(limit=amount)

@client.command()
async def play(ctx, url):
    # Get the voice channel that the user is in
    voice_channel = ctx.author.voice.channel

    # Check if the bot is already in a voice channel
    if ctx.message.guild.id in playlist:
        playlist[ctx.message.guild.id].append({'url': url})
        await ctx.send('Added to playlist.')
        return

    # Join the voice channel
    await voice_channel.connect()

    # Create a new playlist for the server
    playlist[ctx.message.guild.id] = [{'url': url}]

    # Play the song
    await play(ctx, url)

@client.command()
async def queue(ctx):
    server = ctx.message.guild

    # Check if there is a playlist for the server
    if server.id in playlist:
        # Print the playlist
        output = ''
        for i, song in enumerate(playlist[server.id]):
            output += f"{i+1}: {song['url']}\n"
        await ctx.send(output)
    else:
        await ctx.send('The playlist is currently empty.')

@client.command()
async def remove(ctx, index):
    server = ctx.message.guild

    # Check if there is a playlist for the server
    if server.id in playlist:
        # Remove the song from the playlist
        try:
            index = int(index) - 1
            removed_song = playlist[server.id].pop(index)
            await ctx.send(f"Removed {removed_song['url']} from the playlist.")
        except IndexError:
            await ctx.send("Invalid index.")
    else:
        await ctx
