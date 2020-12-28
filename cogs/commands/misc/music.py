import re
import os

import discord
import lavalink
import humanize
import datetime
import traceback
from discord.ext import commands

url_rx = re.compile(r'https?://(?:www\.)?.+')


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.np = None
        self.reactions = ['⏯️', '⏭️', '⏹']
        self.votes = set()
        self.vote_message = None
        self.cur_vc_mems = 0

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
        await self.ensure_voice(ctx)
        #  Ensure that the bot and command author share a mutual voicechannel.

        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and ctx.channel.id != self.channel.id:
            raise commands.BadArgument(
                f"Command only allowed in <#{self.channel.id}>")

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

        # if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
        #     if int(player.channel_id) != ctx.author.voice.channel.id:

        #     if ctx.author.voice.channel.id != self.bot.settings.guild().channel_music:
        #         raise commands.BadArgument("Please join the Music voice channel.")

        if not player.is_connected:
            if not should_connect:
                raise commands.BadArgument("I'm not connected to a voice channel!")

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise commands.BadArgument('I need the `CONNECT` and `SPEAK` permissions.')

            player.store('channel', ctx.channel.id)
            if self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
                await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
            else:
                if ctx.author.voice.channel.id != self.bot.settings.guild().channel_music:
                    raise commands.BadArgument("Please join the Music voice channel.")
                else:
                    await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:
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
            # When this track_hook receives a "QueueEndEvent" from lavalink.py
            # it indicates that there are no tracks left in the player's queue.
            # To save on resources, we can tell the bot to disconnect from the voicechannel.
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
        elif isinstance(event, lavalink.events.TrackStartEvent):
            guild = int(event.player.guild_id)
            await self.do_np(guild)
        elif isinstance(event, lavalink.events.TrackEndEvent):
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

    async def do_np(self, guild):
        player = self.bot.lavalink.player_manager.get(guild)
        track = player.current
        track = player.fetch(track.identifier)
        data = track["info"]

        embed = discord.Embed(title="Now playing...")
        embed.add_field(name="Song", value=f"[{data.get('title')}]({data.get('uri')})", inline=False)
        embed.add_field(name="By", value=data.get('author'))
        embed.add_field(name="Duration", value=humanize.naturaldelta(datetime.timedelta(milliseconds=data.get('length'))))
        embed.color = discord.Color.random()
        self.np = await self.channel.send(embed=embed)

        for r in self.reactions:
            try:
                await self.np.add_reaction(r)
            except Exception:
                return

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
            embed = discord.Embed()
            embed.description = "There's no one in the music channel. Paused the song!"
            embed.color = discord.Color.blurple()
            await self.channel.send(embed=embed, delete_after=5)
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

        player = self.bot.lavalink.player_manager.get(reaction.message.guild.id)
        ctx = self.channel
        if player.channel_id is None:
            return
        if str(reaction.emoji) not in self.reactions:
            return
        else:
            await reaction.message.remove_reaction(reaction, user)

        vc = self.bot.get_channel(int(player.channel_id))
        if user not in vc.members:
            await reaction.message.remove_reaction(reaction, user)
            return

        if str(reaction.emoji) == '⏯️':
            if not player.paused:
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
            if self.vote_message is not None and reaction.message.id == self.vote_message.id:
                if self.bot.settings.permissions.hasAtLeast(ctx.guild, user, 5):
                    embed = discord.Embed()
                    embed.description = f"{user.mention} skipped the song!"
                    embed.color = discord.Color.blurple()
                    await ctx.send(embed=embed)
                    await player.skip()
                    return
                self.votes.add(user.id)
                voice_mem_list = vc.members
                for i, o in enumerate(voice_mem_list):
                    if o.bot: # get list of users in voice, not including bots
                        del voice_mem_list[i]
                self.cur_vc_mems = len(voice_mem_list)
                if len(self.votes) > (self.cur_vc_mems / 2):
                    embed = discord.Embed()
                    embed.description = "Skipped the song!"
                    embed.color = discord.Color.blurple()
                    self.votes.clear()
                    await self.vote_message.delete()
                    self.vote_message = None
                    await ctx.send(embed=embed)
                    await player.skip()
                else:
                    embed = discord.Embed()
                    embed.description = f"({len(self.votes)}/{self.cur_vc_mems}) Skip the song?"
                    embed.color = discord.Color.blurple()
                    await self.vote_message.edit(embed=embed)
            else:
                await player.skip()
                embed = discord.Embed()
                embed.description = f"{user.mention}: Skipped the song!"
                embed.color = discord.Color.blurple()
                await ctx.send(embed=embed, delete_after=5)

        elif str(reaction.emoji) == '⏹':
            player.queue.clear()
            # Stop the current track so Lavalink consumes less resources.
            await player.stop()
            # Disconnect from the voice channel.
            await self.connect_to(user.guild.id, None)
            embed = discord.Embed()
            embed.description = f"Disconnected and cleared queue."
            embed.color = discord.Color.blurple()
            await ctx.send(embed=embed, delete_after=5)

    @commands.command(aliases=['p'])
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

        if not player.is_playing:
            raise commands.BadArgument('I am not currently playing anything!')
        
        def is_bot(user):
            return user.bot
        
        def react_check(reaction, user):
            return reaction.message.id == self.vote_message.id and str(reaction.emoji) == "⏭️" and not user.bot and ctx.me.voice.channel.members.count(user) > 0
        
        voice_mem_list = ctx.me.voice.channel.members
        for i, o in enumerate(voice_mem_list):
            if o.bot: # get list of users in voice, not including bots
                del voice_mem_list[i]
        channel_mem_count = len(voice_mem_list)
        self.cur_vc_mems = len(voice_mem_list)
        print(f"mem ct: {channel_mem_count}")
        
        if self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5) or channel_mem_count <= 1:
            print("bruh?")
            embed = discord.Embed()
            embed.description = f"{ctx.author.mention} skipped the song!"
            embed.color = discord.Color.blurple()
            await ctx.send(embed=embed)
            await player.skip()
        else:
            self.votes.add(ctx.author.id)
            print(f"votes: {self.votes}")
            vote_count = len(self.votes)
            print(f"vote count: {vote_count}")
            if vote_count == 1:
                embed = discord.Embed()
                embed.description = f"(1/{channel_mem_count}) Skip the current song?"
                embed.color = discord.Color.blurple()
                self.vote_message = await ctx.send(embed=embed)
                await self.vote_message.add_reaction("⏭️")
            if vote_count > (channel_mem_count / 2):
                embed = self.vote_message.embeds[0]
                embed.description = f"({vote_count}/{channel_mem_count}) Skipping the song!"
                embed.color = discord.Color.blurple()
                await self.vote_message.delete()
                self.vote_message = None
                await ctx.send(embed=embed)
                await player.skip()
                self.votes.clear()
            else:
                embed = discord.Embed()
                embed.description = f"({vote_count}/{channel_mem_count}) Skip the current song?"
                embed.color = discord.Color.blurple()
                await self.vote_message.edit(embed=embed) 

    @commands.command(name="stop", aliases=['dc'])
    async def disconnect(self, ctx):
        """ Disconnects the player from the voice channel and clears its queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            # We can't disconnect, if we're not connected.
            return await ctx.send('Not connected.')

        # Clear the queue to ensure old tracks don't start playing
        # when someone else queues something.
        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        await self.connect_to(ctx.guild.id, None)
        embed = discord.Embed()
        embed.description = f"Disconnected and cleared queue."
        embed.color = discord.Color.blurple()
        await ctx.send(embed=embed, delete_after=5)

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
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            await self.bot.send_error(ctx, "A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()

def setup(bot):
    bot.add_cog(Music(bot))
