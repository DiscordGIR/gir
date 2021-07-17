import asyncio
import datetime
import os
import re
import traceback
from random import shuffle

import cogs.utils.context as context
import discord
import humanize
import lavalink
import spotipy
from discord.ext import commands, tasks
from spotipy.oauth2 import SpotifyClientCredentials

url_rx = re.compile(r'https?://(?:www\.)?.+')
spotify_track = re.compile(r"[\bhttps://open.\b]*spotify[\b.com\b]*[/:]*track[/:]*[A-Za-z0-9?=]+")
spotify_playlist = re.compile(r"[\bhttps://open.\b]*spotify[\b.com\b]*[/:]*playlist[/:]*[A-Za-z0-9?=]+")


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.now_playing_embed_message = None
        self.reactions = ['⏯️', '⏭️', '⏹']
        
        # set of users that have voted to skip currently playing song
        self.skip_votes = set()
        # message where users are voting to skip
        self.skip_vote_msg = None
        
        # set of users that have voted to clear queue
        self.clear_votes = set()
        # message where users are voting to clear queue
        self.clear_vote_msg = None
        
        # percentage of users in voice channels that need to vote to skip or clear queue
        self.vote_ratio = 0.5

        # spotify API session for queueing spotify songs/playlists
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
                                                           client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET")))

        # initialize music backend (lavalink)
        guild = self.bot.get_guild(self.bot.settings.guild_id)
        self.bot_commands_text_channel = guild.get_channel(self.bot.settings.guild().channel_botspam)
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
        
        # non-mods can only use music commands in #bot-commands channel
        await ctx.message.delete()
        if not ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and ctx.channel.id != self.bot_commands_text_channel.id:
            raise commands.BadArgument(
                f"Command only allowed in <#{self.bot_commands_text_channel.id}>")

        if (await ctx.settings.user(ctx.author.id)).is_music_banned:
            raise commands.BadArgument(f"{ctx.author.mention}, you are banned from using Music commands.")

        # ensure user is connected to a voice channel before allowing them to control bot
        await self.ensure_voice(ctx)
        return guild_check

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """

        # Create returns a player if one exists, otherwise creates.
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        should_connect = ctx.command.name in ('play', 'pause', 'skip', 'resume', 'queue', 'volume', )

        if not ctx.author.voice or not ctx.author.voice.channel:
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
            if ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
                await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
            else:
                if ctx.author.voice.channel.id != ctx.settings.guild().channel_music:
                    raise commands.BadArgument("Please join the Music voice channel.")
                else:
                    await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:  # the bot is connected to a vc
            # the bot should join the user's vc if they are a mod, else tell them to join the same vc
            if int(player.channel_id) != ctx.author.voice.channel.id:
                if ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
                    await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
                else:
                    if int(player.channel_id) == self.bot_commands_text_channel.id:
                        await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
                    else:
                        raise commands.BadArgument('You need to be in my voicechannel.')

    async def track_hook(self, event):
        """This is caled whenever the music backend emits an event (i.e queue ends, track changes). We want to
        customize this behavior."""
        
        if isinstance(event, lavalink.events.QueueEndEvent):
            # queue has ended
            
            # remove current song from bot's status 
            await self.bot.change_presence(status=discord.Status.online, activity=None)
            
            guild_id = int(event.player.guild_id)
            guild = self.bot.get_guild(guild_id)
            
            # disconnect from the voice channel
            # await guild.change_voice_state(channel=None)
            
            # reset votes to skip current song
            self.skip_votes = set()
            if self.skip_vote_msg is not None:
                try:
                    await self.skip_vote_msg.delete()
                except:
                    pass
                finally:
                    self.skip_vote_msg = None
            
            if self.now_playing_embed_message:
                try:
                    await self.now_playing_embed_message.delete()
                except Exception:
                    pass

        elif isinstance(event, lavalink.events.TrackStartEvent):
            # a new track has just started playing
            
            # post embed for this song, change bot playing status
            await self.activities_for_new_song(event)

            await asyncio.sleep(5)
            # start loop to update song progress in embed
            try:
                self.update_current_song_progressbar.start()
            except Exception:
                pass

        elif isinstance(event, lavalink.events.TrackEndEvent):
            # a track has just ended
            
            # reset skip vote, delete skip vote message
            self.skip_votes = set()
            if self.skip_vote_msg is not None:
                try:
                    await self.skip_vote_msg.delete()
                except:
                    pass
                finally:
                    self.skip_vote_msg = None

            # delete the ended song's embed message
            if self.now_playing_embed_message is not None:
                try:
                    await self.now_playing_embed_message.delete()
                except Exception:
                    pass
                
            # stop updating progress for the song that just ended
            try:
                self.update_current_song_progressbar.cancel()
            except Exception:
                pass

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """This function is run every time someone joines or leaves a voice channel.
        We want to pause the player if there are no users in the music channel and
        resume if someone joins and the player was paused.

        Parameters
        ----------
        member : discord.Member
            whoever just joined or left the voice channel
        before : ignored
        after : ignored
        """
        
        if member.bot:
            return

        player = self.bot.lavalink.player_manager.get(member.guild.id)
        if player is None or player.channel_id is None:
            return

        guild = self.bot.get_guild(int(player.guild_id))
        chan = guild.get_channel(int(player.channel_id))
        
        # is the bot alone in the music channel now?
        if len(chan.members) == 1 and chan.members[0].id == self.bot.user.id:
            # yes! pause the player
            await player.set_pause(True)
            # stop updating song progress in embed
            try:
                self.update_current_song_progressbar.stop()
            except Exception:
                pass
            # reset bot's status
            await self.bot.change_presence(status=discord.Status.online, activity=None)
            
        # is the bot not alone in the voice channel?
        elif len(chan.members) > 1:
            # yes. we want to resume the player if it was paused.
            if player.paused:
                await player.set_pause(False)
                # resume updating song progress in embed
                try:
                    self.update_current_song_progressbar.start()
                except Exception:
                    pass
                
                # notify whoever joined that we're resuming.
                embed = discord.Embed()
                embed.description = "The player was paused because no one was in the voice channel. Resuming previous!"
                embed.color = discord.Color.blurple()
                await self.bot_commands_text_channel.send(member.mention, embed=embed, delete_after=10)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Watch for reaction events. We have an embed which has play, pause, skip controls
        using reactions. This handles the actions when the reaction is added."""
        
        # constraints to ignore depending on who reacted
        if user.bot:
            return
        if reaction.message.guild is None:
            return
        if reaction.message.author.id != self.bot.user.id:
            return
        if reaction.message.channel.id != self.bot_commands_text_channel.id:
            return
        
        # ignore if reactor is music banned
        if (await self.bot.settings.user(user.id)).is_music_banned:
            await reaction.message.remove_reaction(reaction, user)
            return

        # get player, if player not playing, nothing to do.
        player = self.bot.lavalink.player_manager.get(reaction.message.guild.id)
        if player is None:
            return
        if player.channel_id is None:
            return
        
        # break if not a recognized control emoji
        if str(reaction.emoji) not in self.reactions:
            return
        
        if player.current is None:
            return

        # check if the reactor is in music channel
        vc = self.bot.get_channel(int(player.channel_id))
        if user not in vc.members:
            return
        
        await reaction.message.remove_reaction(reaction, user)

        # alright! we passed all the constraints. now let's handle the controls
        if str(reaction.emoji) == '⏯️':
            # toggle play/pause status
            embed = discord.Embed(color=discord.Color.blurple())
            await player.set_pause(not player.paused)
            
            if player.paused:
                await self.bot.change_presence(status=discord.Status.online, activity=None)
                embed.description = f"{user.mention}: Paused the song!"
                await self.bot_commands_text_channel.send(embed=embed, delete_after=5)

            else:
                embed.description = f"{user.mention}: Resumed the song!"
                await self.bot_commands_text_channel.send(embed=embed, delete_after=5)

                track = player.current
                if track is None:
                    return
                track = player.fetch(track.identifier)
                title = track["info"].get('title')
                if title is not None:
                    activity = discord.Activity(type=discord.ActivityType.listening, name=title)
                    await self.bot.change_presence(status=discord.Status.online, activity=activity)

        elif str(reaction.emoji) == '⏭️':
            await self.do_skip(reaction.message.channel, user, player)

        elif str(reaction.emoji) == '⏹':
            await self.do_clear(reaction.message.channel, user, player)
           
    async def connect_to(self, guild_id: int, channel_id: str):
        """ Connects to the given voicechannel ID. A channel_id of `None` means disconnect. """
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    async def activities_for_new_song(self, event, post_reactions=True):
        """This is run every time a new song is played. It posts embed of this song in #bot-commands,
        sets the bot status, starts song progress updating loop"""
        
        guild = int(event.player.guild_id)
        player = self.bot.lavalink.player_manager.get(guild)
        track = player.current
        if track is None or not player.is_playing:
            raise commands.BadArgument('I am not currently playing anything!')
        track = player.fetch(track.identifier)
        data = track["info"]
        embed = discord.Embed(title="Now playing...")
        embed.add_field(name="Song", value=f"[{data.get('title')}]({data.get('uri')})", inline=False)
        embed.add_field(name="By", value=data.get('author'))
        embed.add_field(name="Duration", value=humanize.naturaldelta(datetime.timedelta(milliseconds=data.get('length'))))
        embed.add_field(name="Requested by", value=f"<@{player.current.requester}>")

        progress = self.get_progress(player, data)
        embed.add_field(name="Progress", value=progress)
        embed.color = discord.Color.random()
        
        if not post_reactions:
            await self.bot_commands_text_channel.send(embed=embed, delete_after=10)
        else:
            msg = await self.bot_commands_text_channel.send(embed=embed)
            self.now_playing_embed_message = msg
            for r in self.reactions:
                try:
                    await msg.add_reaction(r)
                except Exception as e:
                    return
        
        title = data.get('title')
        if title is not None:
            activity = discord.Activity(type=discord.ActivityType.listening, name=title)
            await self.bot.change_presence(status=discord.Status.online, activity=activity)

    def get_progress(self, player, data):
        """Generates a string with a fancy progress bar made of emojis for currently playing song"""
        length = int(data.get('length'))
        position = int(player.position)
        p = int(position / length * 100) if position != length else 0

        def fix_emojis(desc):
            custom_emojis = re.findall(r':\w*:', desc)
            new = ""
            for e in custom_emojis:
                e = e.replace(':', '')
                replacement = discord.utils.get(self.bot.emojis, name=e)
                if replacement is not None:
                    new = new + str(replacement)
            return new

        percentage = int(((position / length) * 100 / 10) ) if position != length else 0
        if percentage == 0:
            progress = f":progress1:{':progressempty:' * 8}:progressempty2:"
        elif percentage == 10:
            progress = f":progress1:{'progress2:' * 8}:progress3:"
        else:
            progress = f":progress1:{':progress2:' * percentage}{':progressempty:' * (8 - percentage)}:progressempty2:"

        return str(p) + "% " + fix_emojis(progress)

    @tasks.loop(seconds=20)
    async def update_current_song_progressbar(self):
        player = self.bot.lavalink.player_manager.get(self.bot_commands_text_channel.guild.id)
        if self.now_playing_embed_message is None:
            return
        if player is None:
            return
        track = player.current
        if track is None or not player.is_playing:
            return
        track = player.fetch(track.identifier)
        data = track["info"]

        embed = self.now_playing_embed_message.embeds[0]
        embed.set_field_at(4, name="Progress", value=self.get_progress(player, data))

        try:
            await self.now_playing_embed_message.edit(embed=embed)
        except Exception:
            pass

    async def do_skip(self, channel, skipper, player):
        """Helper function to handle skipping song"""

        if not player.is_playing:
            raise commands.BadArgument('I am not currently playing anything!')

        # bypass vote if skipper is a mod or original requester of the song.
        if int(player.current.requester) != skipper.id and not self.bot.settings.permissions.hasAtLeast(channel.guild, skipper, 5):
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
                self.skip_vote_msg = await self.bot_commands_text_channel.send(embed=embed)
                return

        await player.skip()
        embed = discord.Embed()
        embed.description = f"{skipper.mention}: Skipped the song!"
        embed.color = discord.Color.blurple()
        await channel.send(embed=embed, delete_after=5)

    async def do_clear(self, channel, clearer, player):
        """Helper function to handle clearing queue"""

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
                self.clear_vote_msg = await self.bot_commands_text_channel.send(embed=embed)
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

    @commands.command(aliases=['p'])
    @commands.cooldown(2, 10, commands.BucketType.member)
    async def play(self,  ctx: context.Context, *, query: str):
        """Plays song/playlist from YouTube/Spotify URL, URI or search term.

        Example usage
        -------------
        !play xo tour llif3

        Parameters
        ----------
        query : str
            "Search term, or Spotify/YouTube URL"
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
        await self.activities_for_new_song(ctx.guild.id, post_reactions=False)

    @commands.guild_only()
    @commands.command(name='queue', aliases=['q', 'playlist'])
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""

        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if len(player.queue) == 0:
            raise commands.BadArgument('There are currently no more queued songs.')

        # Grab up to 5 entries from the queue...
        upcoming = player.queue[0:5]

        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}')
        embed.color = discord.Color.blurple()
        for i, song in enumerate(upcoming):
            embed.add_field(name=f"{i+1}. {song.title}", value=f"Requested by <@{song.requester}>", inline=False)
        embed.set_footer(text=f"{len(upcoming)} songs out of {len(player.queue)}")
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(name='volume', aliases=['vol'])
    async def change_volume(self,  ctx: context.Context, *, vol: int):
        """Change the player volume.

        Example usage
        -------------
        !volume 100

        Parameters
        ------------
        volume: int
            "The volume to set the player to in percentage. This must be between 1 and 100."
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

    @commands.guild_only()
    @commands.command(name='shuffle')
    async def shuffle_(self, ctx):
        """Shuffle the queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        shuffle(player.queue)
        await ctx.send("Shuffled queue.")

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
    @shuffle_.error
    async def info_error(self,  ctx: context.Context, error):
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
            await ctx.send_error(error)
        else:
            await ctx.send_error("A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()

def setup(bot):
    bot.add_cog(Music(bot))
