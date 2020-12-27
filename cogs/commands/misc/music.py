"""
Please understand Music bots are complex, and that even this basic example can be daunting to a beginner.

For this reason it's highly advised you familiarize yourself with discord.py, python and asyncio, BEFORE
you attempt to write a music bot.

This example makes use of: Python 3.6

For a more basic voice example please read:
    https://github.com/Rapptz/discord.py/blob/rewrite/examples/basic_voice.py

This is a very basic playlist example, which allows per guild playback of unique queues.
The commands implement very basic logic for basic usage. But allow for expansion. It would be advisable to implement
your own permissions and usage logic for commands.

e.g You might like to implement a vote before skipping the song or only allow admins to stop the player.

Music bots require lots of work, and tuning. Goodluck.
If you find any bugs feel free to ping me on discord. @Eviee#0666
"""
import discord
from discord.ext import commands

import asyncio
import itertools
import sys
import traceback
import humanize
import datetime
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL


ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')
        self.data = data

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.

        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        data = ytdl.extract_info(url=search, download=False)
        if 'entries' in data:
            # take first item from a playlist
            if len(data['entries']) == 0:
                raise commands.BadArgument("No results found.")
            data = data['entries'][0]
        if int(data["duration"]) > 3600:
            raise commands.BadArgument("That song is too long. Max length is 1 hour.")

        to_run = partial(ytdl.extract_info, url=search, download=False)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        embed = discord.Embed(title="Added to queue")
        embed.add_field(name="Song", value=f"[{data['title']}]({data['webpage_url']})", inline=False)
        embed.add_field(name="By", value=data.get('uploader'))
        embed.add_field(name="Duration", value=humanize.naturaldelta(datetime.timedelta(seconds=data.get('duration'))))
        embed.set_thumbnail(url=data.get("thumbnail"))
        embed.color = discord.Color.random()

        await ctx.send(embed=embed, delete_after=5)

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.

        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer():
    """A class which is assigned to each guild using the bot for Music.

    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.

    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, bot, guild, channel, cog):
        self.bot = bot
        self._guild = guild
        self._channel = channel
        self._cog = cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None

        self.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            self.np = await self._channel.send(embed=await self.song_embed(source))
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            import gc
            gc.collect()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    async def song_embed(self, source):
        embed = discord.Embed(title="Now playing...")
        embed.add_field(name="Song", value=f"[{source.title}]({source.web_url})", inline=False)
        embed.add_field(name="By", value=source.data.get('uploader'))
        embed.add_field(name="Duration", value=humanize.naturaldelta(datetime.timedelta(seconds=source.data.get('duration'))))
        embed.add_field(name="Requested by", value=source.requester.mention)
        embed.set_thumbnail(url=source.data.get("thumbnail"))
        embed.color = discord.Color.random()
        return embed

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):
    """Music related commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            guild = self.bot.get_guild(self.bot.settings.guild_id)
            channel = guild.get_channel(778233669881561088)
            player = MusicPlayer(self.bot, guild, channel, self)
            self.players[ctx.guild.id] = player

        return player

    @commands.guild_only()
    @commands.command(name='connect', aliases=['join'])
    async def connect_(self, ctx, *, channel: discord.VoiceChannel = None):
        """Connect to voice.

        Parameters
        ------------
        channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.

        This command also handles moving the bot to different channels.
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')

        await ctx.send(f'Connected to: **{channel}**', delete_after=20)

    @commands.guild_only()
    @commands.command(name='play', aliases=['sing'])
    async def play_(self, ctx, *, search: str):
        """Request a song and add it to the queue.

        This command attempts to join a valid voice channel if the bot is not already in one.
        Uses YTDL to automatically search and retrieve a song.

        Parameters
        ------------
        search: str [Required]
            The song to search and retrieve using YTDL. This could be a simple search, an ID or URL.
        """
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=True)

        await player.queue.put(source)

    @commands.guild_only()
    @commands.command(name='pause')
    async def pause_(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            raise commands.BadArgument('I am not currently playing anything!')
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f'**`{ctx.author}`**: Paused the song!')

    @commands.guild_only()
    @commands.command(name='resume')
    async def resume_(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            raise commands.BadArgument('I am not currently playing anything!')
        elif not vc.is_paused():
            return

        vc.resume()

    @commands.guild_only()
    @commands.command(name='skip')
    async def skip_(self, ctx):
        """Skip the song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            raise commands.BadArgument('I am not currently playing anything!')

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send(f'**`{ctx.author}`**: Skipped the song!', delete_after=10)

    @commands.guild_only()
    @commands.command(name='queue', aliases=['q', 'playlist'])
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            raise commands.BadArgument('I am not currently connected to voice!')

        player = self.get_player(ctx)
        if player.queue.empty():
            raise commands.BadArgument('There are currently no more queued songs.')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = '\n'.join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}')
        embed.color = discord.Color.blurple()
        for i, song in enumerate(upcoming):
            embed.add_field(name=f"{i+1}. {song.title}", value=f"Requested by {song.requester.mention}", inline=False)

        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(name='volume', aliases=['vol'])
    async def change_volume(self, ctx, *, vol: float):
        """Change the player volume.

        Parameters
        ------------
        volume: float or int [Required]
            The volume to set the player to in percentage. This must be between 1 and 100.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            raise commands.BadArgument('I am not currently connected to voice!')

        if not 0 < vol < 101:
            raise commands.BadArgument('Please enter a value between 1 and 100.')

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        embed = discord.Embed()
        embed.description = f'{ctx.author.mention} set the volume to **{vol}%**'
        embed.color = discord.Color.blurple()
        await ctx.send(embed=embed, delete_after=5)

    @commands.guild_only()
    @commands.command(name='stop')
    async def stop_(self, ctx):
        """Stop the currently playing song and destroy the player.

        !Warning!
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            raise commands.BadArgument('I am not currently playing anything!')

        await self.cleanup(ctx.guild)

    @resume_.error
    @pause_.error
    @queue_info.error
    @change_volume.error
    @stop_.error
    @play_.error
    async def info_error(self, ctx, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            await self.bot.send_error(ctx, "A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Music(bot))
