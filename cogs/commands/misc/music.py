import re
import os

import discord
import lavalink
import humanize
import datetime
import traceback
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

url_rx = re.compile(r'https?://(?:www\.)?.+')
spotify_track = re.compile(r"[\bhttps://open.\b]*spotify[\b.com\b]*[/:]*track[/:]*[A-Za-z0-9?=]+")
spotify_playlist = re.compile(r"[\bhttps://open.\b]*spotify[\b.com\b]*[/:]*playlist[/:]*[A-Za-z0-9?=]+")


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.np = None
        self.reactions = ['⏯️', '⏭️', '⏹']
        self.skip_votes = set()
        self.skip_vote_msg = None
        self.clear_votes = set()
        self.clear_vote_msg = None
        self.vote_ratio = 0.5

        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
                                                           client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET")))

        guild = self.bot.get_guild(self.bot.settings.guild_id)
        self.channel = guild.get_channel(self.bot.settings.guild().channel_botspam)
        if not hasattr(bot, 'lavalink'):  # This ensures the client isn't overwritten during cog reloads.
            bot.lavalink = lavalink.Client(self.bot.user.id)
            bot.lavalink.add_node('127.0.0.1', 2333, os.environ.get("LAVALINK_PASS"), guild.region, 'default-node')  # Host, Port, Password, Region, Name
            bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')

        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        """ Command before-invoke handler. """
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if not guild_check:
            return False

        await ctx.message.delete()
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and ctx.channel.id != self.channel.id:
            raise commands.BadArgument(
                f"Command only allowed in <#{self.channel.id}>")

        if (await self.bot.settings.user(ctx.author.id)).is_music_banned:
            raise commands.BadArgument(f"{ctx.author.mention}, you are banned from using Music commands.")

        await self.ensure_voice(ctx)
        return guild_check

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        should_connect = ctx.command.name in ('play', 'pause', 'skip', 'resume', 'queue', 'volume', )

        if not ctx.author.voice or not ctx.author.voice.channel:
            # Our cog_command_error handler catches this and sends it to the voicechannel.
            # Exceptions allow us to "short-circuit" command invocation via checks so the
            # execution state of the command goes no further.
            raise commands.CommandInvokeError('Join a voicechannel first.')

        # check if bot is connected to a voice channel
        if not player.is_connected:
            if not should_connect:
                raise commands.BadArgument("I'm not connected to a voice channel!")

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise commands.BadArgument('I need the `CONNECT` and `SPEAK` permissions.')

            player.store('channel', ctx.channel.id)

            # if the user is mod, join regardless of what channel they're in
            # else, tell them to use the Music channel.
            # only mods can move the bot
            if self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
                await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
            else:
                if ctx.author.voice.channel.id != self.bot.settings.guild().channel_music:
                    raise commands.BadArgument("Please join the Music voice channel.")
                else:
                    await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:  # the bot is connected to a vc
            # the bot should join the user's vc if they are a mod, else tell them to join the same vc
            if int(player.channel_id) != ctx.author.voice.channel.id:
                if self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
                    await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
                else:
                    if int(player.channel_id) == self.channel.id:
                        await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
                    else:
                        raise commands.BadArgument('You need to be in my voicechannel.')

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            await self.bot.change_presence(status=discord.Status.online, activity=None)
        elif isinstance(event, lavalink.events.TrackStartEvent):
            guild = int(event.player.guild_id)
            await self.do_np(guild)
            
            track = event.player.current
            track = event.player.fetch(track.identifier)
            title = track["info"].get('title')
            if title is not None:
                activity = discord.Activity(type=discord.ActivityType.listening, name=title)
                await self.bot.change_presence(status=discord.Status.online, activity=activity)
        elif isinstance(event, lavalink.events.TrackEndEvent):
            self.skip_votes = set()
            self.skip_vote_msg = None
            self.clear_votes = set()
            self.clear_vote_msg = None
            if self.np:
                try:
                    await self.np.delete()
                except Exception:
                    pass

    async def connect_to(self, guild_id: int, channel_id: str):
        """ Connects to the given voicechannel ID. A channel_id of `None` means disconnect. """
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)
        # The above looks dirty, we could alternatively use `bot.shards[shard_id].ws` but that assumes
        # the bot instance is an AutoShardedBot.

    async def do_np(self, guild, post_reactions=True):
        player = self.bot.lavalink.player_manager.get(guild)
        track = player.current
        track = player.fetch(track.identifier)
        data = track["info"]

        embed = discord.Embed(title="Now playing...")
        embed.add_field(name="Song", value=f"[{data.get('title')}]({data.get('uri')})", inline=False)
        embed.add_field(name="By", value=data.get('author'))
        embed.add_field(name="Duration", value=humanize.naturaldelta(datetime.timedelta(milliseconds=data.get('length'))))
        embed.add_field(name="Requested by", value=f"<@{player.current.requester}>")
        embed.color = discord.Color.random()
        
        if not post_reactions:
            await self.channel.send(embed=embed, delete_after=10)
        else:
            self.np = await self.channel.send(embed=embed)

            for r in self.reactions:
                try:
                    await self.np.add_reaction(r)
                except Exception:
                    return

    async def do_skip(self, channel, skipper, player):
        if not player.is_playing:
            raise commands.BadArgument('I am not currently playing anything!')

        if not self.bot.settings.permissions.hasAtLeast(channel.guild, skipper, 5):
            vc = channel.guild.get_channel(int(player.channel_id))
            num_in_vc = len(list(filter(lambda m: not m.bot, vc.members)))
            self.skip_votes.add(skipper)

            if self.skip_vote_msg is not None:
                try:
                    await self.skip_vote_msg.delete()
                except Exception:
                    pass

            if len(self.skip_votes) / num_in_vc < self.vote_ratio:
                embed = discord.Embed(title="Vote skip")
                embed.add_field(name="Vote skip", value=f"{len(self.skip_votes)} out of {num_in_vc} have voted to skip. We need more than {int(self.vote_ratio * num_in_vc)}.")
                embed.color = discord.Color.green()
                self.skip_vote_msg = await self.channel.send(embed=embed)
                return

        await player.skip()
        embed = discord.Embed()
        embed.description = f"{skipper.mention}: Skipped the song!"
        embed.color = discord.Color.blurple()
        await channel.send(embed=embed, delete_after=5)
    
    async def do_clear(self, channel, clearer, player):
        if not player.is_playing:
            raise commands.BadArgument('I am not currently playing anything!')

        if not self.bot.settings.permissions.hasAtLeast(channel.guild, clearer, 5):
            vc = channel.guild.get_channel(int(player.channel_id))
            num_in_vc = len(list(filter(lambda m: not m.bot, vc.members)))
            self.clear_votes.add(clearer)

            if self.clear_vote_msg is not None:
                try:
                    await self.clear_vote_msg.delete()
                except Exception:
                    pass

            if len(self.clear_votes) / num_in_vc < self.vote_ratio:
                embed = discord.Embed(title="Vote skip")
                embed.add_field(name="Vote skip", value=f"{len(self.clear_votes)} out of {num_in_vc} have voted to clear the queue. We need more than {int(self.vote_ratio * num_in_vc)}.")
                embed.color = discord.Color.green()
                self.clear_vote_msg = await self.channel.send(embed=embed)
                return

        # Clear the queue to ensure old tracks don't start playing
        # when someone else queues something.
        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        embed = discord.Embed()
        embed.description = f"Cleared queue."
        embed.color = discord.Color.blurple()
        await channel.send(embed=embed, delete_after=5)


    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        player = self.bot.lavalink.player_manager.get(member.guild.id)
        if player is None or player.channel_id is None:
            return
        if member.bot:
            return

        chan = self.bot.get_channel(int(player.channel_id))
        if len(chan.members) == 1 and chan.members[0].id == self.bot.user.id:
            await player.set_pause(True)
            await self.bot.change_presence(status=discord.Status.online, activity=None)
            embed = discord.Embed()
            embed.description = "There's no one in the music channel. Paused the song!"
            embed.color = discord.Color.blurple()
            await self.channel.send(embed=embed)
        elif len(chan.members) > 1:
            if player.paused:
                await player.set_pause(False)
                embed = discord.Embed()
                embed.description = "Resuming previous!"
                embed.color = discord.Color.blurple()
                await self.channel.send(embed=embed, delete_after=5)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        if reaction.message.guild is None:
            return
        if reaction.message.author.id != self.bot.user.id:
            return
        if reaction.message.channel.id != self.channel.id:
            return
        if (await self.bot.settings.user(user.id)).is_music_banned:
            await reaction.message.remove_reaction(reaction, user)
            return

        player = self.bot.lavalink.player_manager.get(reaction.message.guild.id)
        ctx = self.channel
        if player.channel_id is None:
            return
        if str(reaction.emoji) not in self.reactions:
            await reaction.message.remove_reaction(reaction, user)
            return

        vc = self.bot.get_channel(int(player.channel_id))
        if user not in vc.members:
            await reaction.message.remove_reaction(reaction, user)
            return

        if str(reaction.emoji) == '⏯️':
            if not player.paused:
                await self.bot.change_presence(status=discord.Status.online, activity=None)
                await player.set_pause(True)
                embed = discord.Embed()
                embed.description = f"{user.mention}: Paused the song!"
                embed.color = discord.Color.blurple()
                await ctx.send(embed=embed, delete_after=5)
            else:
                await player.set_pause(False)
                embed = discord.Embed()
                embed.description = f"{user.mention}: Resumed the song!"
                embed.color = discord.Color.blurple()
                await ctx.send(embed=embed, delete_after=5)

        elif str(reaction.emoji) == '⏭️':
            await self.do_skip(reaction.message.channel, user, player)

        elif str(reaction.emoji) == '⏹':
            await self.do_clear(reaction.message.channel, user, player)

    @commands.command(aliases=['p'])
    @commands.cooldown(2, 10, commands.BucketType.member)
    async def play(self, ctx, *, query: str):
        """Plays song from YouTube link or search term.

        Example usage
        -------------
        `!play xo tour llif3`

        Parameters
        ----------
        query : str
            Search term
        """

        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
        query = query.strip('<>')
        if spotify_track.match(query):
            track = self.sp.track(query)
            query = f"ytsearch:{track['name']} - {track['artists'][0]['name']}"
            # Get the results for the query from Lavalink.
            results = await player.node.get_tracks(query)
        elif spotify_playlist.match(query):
            playlist = self.sp.playlist(query, fields='name,tracks.items.track.name,tracks.items.track.artists')
            results = {'loadType': "PLAYLIST_LOADED", 'tracks': [], 'playlistInfo':  {'name': playlist['name']}}
            
            async with ctx.channel.typing():
                for track in playlist['tracks']['items']:
                    track = track['track']
                    query = f"ytsearch:{track['name']} - {track['artists'][0]['name']}"
                    result = await player.node.get_tracks(query)
                    results['tracks'].append(result['tracks'][0])
                    results['playlistInfo']
        else:
            if not url_rx.match(query):
                query = f'ytsearch:{query}'
            # Get the results for the query from Lavalink.
            results = await player.node.get_tracks(query)

        # Results could be None if Lavalink returns an invalid response (non-JSON/non-200 (OK)).
        # ALternatively, resullts['tracks'] could be an empty array if the query yielded no tracks.
        if not results or not results['tracks']:
            raise commands.BadArgument("Couldn't find a suitable video to play.")

        embed = discord.Embed(color=discord.Color.blurple())

        # Valid loadTypes are:
        #   TRACK_LOADED    - single video/direct URL)
        #   PLAYLIST_LOADED - direct URL to playlist)
        #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
        #   NO_MATCHES      - query yielded no results
        #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']

            for track in tracks:
                # Add all of the tracks from the playlist to the queue.
                player.add(requester=ctx.author.id, track=track)
                player.store(track["info"]["identifier"], track)

            embed.title = 'Playlist Enqueued!'
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            track = results['tracks'][0]
            embed.title = 'Track Enqueued'
            data = track["info"]
            embed = discord.Embed(title="Added to queue")
            embed.add_field(name="Song", value=f"[{data.get('title')}]({data.get('uri')})", inline=False)
            embed.add_field(name="By", value=data.get('author'))
            embed.add_field(name="Duration", value=humanize.naturaldelta(datetime.timedelta(milliseconds=data.get('length'))))
            embed.color = discord.Color.random()

            # You can attach additional information to audiotracks through kwargs, however this involves
            # constructing the AudioTrack class yourself.
            player.store(data["identifier"], track)
            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)

        await ctx.send(embed=embed, delete_after=5)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not player.is_playing:
            await player.play()

    @commands.guild_only()
    @commands.command(name='nowplaying', aliases=['np'])
    async def now_playing(self, ctx):
        """Show which song is currently playing"""
        await self.do_np(ctx.guild.id, post_reactions=False)
    
    @commands.guild_only()
    @commands.command(name='queue', aliases=['q', 'playlist'])
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        # vc = ctx.voice_client

        # if not vc or not vc.is_connected():
            # raise commands.BadArgument('I am not currently connected to voice!')

        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if len(player.queue) == 0:
            raise commands.BadArgument('There are currently no more queued songs.')

        # Grab up to 5 entries from the queue...
        upcoming = player.queue[0:5]

        # fmt = '\n'.join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}')
        embed.color = discord.Color.blurple()
        for i, song in enumerate(upcoming):
            embed.add_field(name=f"{i+1}. {song.title}", value=f"Requested by <@{song.requester}>", inline=False)
        embed.set_footer(text=f"{len(upcoming)} songs out of {len(player.queue)}")
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(name='volume', aliases=['vol'])
    async def change_volume(self, ctx, *, vol: int):
        """Change the player volume.

        Example usage
        -------------
        `!volume 100`

        Parameters
        ------------
        volume: int
            The volume to set the player to in percentage. This must be between 1 and 100.
        """

        if not 0 < vol < 101:
            raise commands.BadArgument('Please enter a value between 1 and 100.')

        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        await player.set_volume(vol)
        embed = discord.Embed()
        embed.description = f'{ctx.author.mention} set the volume to **{vol}%**'
        embed.color = discord.Color.blurple()
        await ctx.send(embed=embed, delete_after=5)

    @commands.guild_only()
    @commands.command(name='pause')
    async def pause_(self, ctx):
        """Pause the currently playing song."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            raise commands.BadArgument('I am not currently playing anything!')

        await player.set_pause(True)
        await self.bot.change_presence(status=discord.Status.online, activity=None)
        embed = discord.Embed()
        embed.description = f"{ctx.author.mention}: Paused the song!"
        embed.color = discord.Color.blurple()
        await ctx.send(embed=embed, delete_after=5)

    @commands.guild_only()
    @commands.command(name='resume')
    async def resume_(self, ctx):
        """Resume the currently paused song."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            raise commands.BadArgument('I am not currently playing anything!')

        await player.set_pause(False)

    @commands.guild_only()
    @commands.command(name='skip')
    async def skip_(self, ctx):
        """Skip the song."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        await self.do_skip(ctx.channel, ctx.author, player)


    @commands.command(name="clear", aliases=['clearqueue'])
    async def disconnect(self, ctx):
        """ Disconnects the player from the voice channel and clears its queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            # We can't disconnect, if we're not connected.
            return await ctx.send('Not connected.')

        await self.do_clear(ctx.channel, ctx.author, player)

    @now_playing.error
    @resume_.error
    @pause_.error
    @disconnect.error
    @change_volume.error
    @queue_info.error
    @skip_.error
    @play.error
    async def info_error(self, ctx, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.CommandInvokeError)
            or isinstance(error, commands.CommandOnCooldown)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            await self.bot.send_error(ctx, "A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()

def setup(bot):
    bot.add_cog(Music(bot))
