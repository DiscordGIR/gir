import discord
from discord.ext import commands
import traceback
import io
import itertools
import asyncio
import textwrap
from math import ceil
from PIL import Image, ImageDraw, ImageFont, ImageOps

from cogs.commands.hungergames.default_players import default_players
from cogs.commands.hungergames.hungergames import HungerGames
from cogs.commands.hungergames.enums import ErrorCode

class HungerGamesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_instance = HungerGames()
        self.pfp_map = {}

    async def produce_leaderboard_image(self, ctx, title, lines):
        max_width = 6
        line_count = 4
        title_height = 0
        
        title_font = ImageFont.truetype('Arial.ttf', 36)
        
        _, title_height = title_font.getsize(title)

        font = ImageFont.truetype('Arial.ttf', 24)
        text_height = 0
        
        
        member = lines[0]
        _, height1 = font.getsize(member.name)
        _, height2 = font.getsize("Alive")
        _, height3 = font.getsize(str(member.kills))
        text_height = (height1 + height2 + height3) * line_count

        ROW_HEIGHT = 175
        ROW_PADDING = 75
        BETWEEN_IMAGE_PADDING = 50
        IMAGE_WIDTH = 100  + (max_width * 150) + (BETWEEN_IMAGE_PADDING*(max_width)) + (max_width // 3)*20 + 100
        IMAGE_HEIGHT = title_height + text_height + (ROW_HEIGHT+ROW_PADDING+10)*(line_count)

        fill = "#000"

        image = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), fill) # RGB, RGBA (with alpha), L (grayscale), 1 (black & white)

        # create object for drawing
        draw = ImageDraw.Draw(image)

        # draw text in center
        current_y = 24
        # text = line["message"]
        width, height = title_font.getsize(title)
        draw.text(((IMAGE_WIDTH - width)//2, current_y), title, font=title_font)
        current_y += height        
        
        current_x = 120
        current_y += ROW_PADDING
        col_width = (IMAGE_WIDTH - 200 ) // max_width - BETWEEN_IMAGE_PADDING
        pfps_added = 0
        for i, member in enumerate(lines):
            pfps_added += 1
            pfp = self.pfp_map.get(member.id)
            if pfp is None:
                user = ctx.guild.get_member(member.id)
                pfp = user.avatar_url_as(format="png", size=128)
            self.pfp_map[member.id] = pfp
            pfp = Image.open(io.BytesIO(await pfp.read()))
            if "Fallen" in title:
                pfp = pfp.convert('L')
            pfp = pfp.resize((128,128), Image.ANTIALIAS)
            pfp = ImageOps.expand(pfp, border=(5,5), fill="#b56204")
            if not member.alive:
                pfp = pfp.convert('L')
            image.paste(pfp, (current_x, current_y))
            
            width, height = font.getsize(member.name)
            draw.text((current_x - 10 + ((col_width - width)//2) ,current_y + 128 + height1), member.name, font=font)
            # draw.text(((current_x + (pfps_added % 6)+col_width)//2, current_y + 128 + height1), member.name, font=font)
            width, height = font.getsize("Alive" if member.alive else "Dead")
            draw.text((current_x - 10 + ((col_width - width)//2), current_y + 8 + 128 + height1 + height2), "Alive" if member.alive else "Dead", font=font, fill="#32a852" if member.alive else "#ff4040")
            
            width, height = font.getsize(f"{member.kills} kills")
            draw.text((current_x - 10 + ((col_width - width)//2), current_y + 16 + 128 + height1 + height2 + height3), f"{member.kills} kills", font=font)
            
            current_x += col_width + BETWEEN_IMAGE_PADDING
            
            if pfps_added % 6 == 0:
                current_x = 120
                current_y += ROW_PADDING + 200

        # create buffer
        buffer = io.BytesIO()

        # save PNG in buffer
        image.save(buffer, format='PNG')    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)
        
        return discord.File(buffer, 'myimage.png')
    
    async def produce_image(self, ctx, title, lines, max_width):
        if max_width < 3:
            max_width = 3

        title_height = 0
        
        title_lines = textwrap.wrap(title, width=15*max_width)
        title_font = ImageFont.truetype('Arial.ttf', 36)
        
        for title_line in title_lines:
            _, height = title_font.getsize(title_line)
            title_height += height

        font = ImageFont.truetype('Arial.ttf', 24)
        text_height = 0
        
        
        line_count = 0
        for line in lines:
            if line is None: 
                continue
            line_count += 1
            text_lines = textwrap.wrap(line["message"], width=15*max_width if max_width > 1 else 30)
            for text_line in text_lines:
                _, height = font.getsize(text_line)
                text_height += height

        ROW_HEIGHT = 160
        ROW_PADDING = 45
        IMAGE_WIDTH = 100  + (max_width * 150) + 100
        IMAGE_HEIGHT = title_height + text_height + (ROW_HEIGHT+ROW_PADDING+10)*line_count

        if line_count == 1:
            IMAGE_HEIGHT += 50

        if "Day" in title:
            fill = "#3285a8"
        elif "Bloodbath" in title:
            fill = "#7a2415"
        elif "Night" in title:
            fill = "#0f3c4f"
        elif "Arena Event" in title:
            fill = "#eb3483"
        else:
            fill = "#000"

        image = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), fill) # RGB, RGBA (with alpha), L (grayscale), 1 (black & white)

        # create object for drawing
        draw = ImageDraw.Draw(image)

        # draw text in center
        current_y = 24
        # text = line["message"]
        for title_line in title_lines:
            width, height = title_font.getsize(title_line)
            draw.text(((IMAGE_WIDTH - width)//2, current_y), title_line, font=title_font)
            current_y += height        
        
        current_y += ROW_PADDING
                
        for line in lines:
            if line is None: continue
            offset = (max_width - (len(line["members"]))) * 75
            for i, member in enumerate(line["members"]):
                col_width = 150
                current_x = offset + (i * col_width ) + 100
                pfp = self.pfp_map.get(member)
                if pfp is None:
                    user = ctx.guild.get_member(member)
                    pfp = user.avatar_url_as(format="png", size=128)
                self.pfp_map[member] = pfp
                pfp = Image.open(io.BytesIO(await pfp.read()))
                if "Fallen" in title:
                    pfp = pfp.convert('L')
                pfp = pfp.resize((128,128), Image.ANTIALIAS)
                pfp = ImageOps.expand(pfp, border=(5,5), fill="#b56204")
                image.paste(pfp, (current_x, current_y))
                
            current_y += 150
            text_lines = textwrap.wrap(line["message"], width=15*max_width if max_width > 1 else 30)
            for text_line in text_lines:
                width, height = font.getsize(text_line)
                draw.text(((image.width - width)//2, current_y), text_line, font=font)
                current_y += height
            current_y += ROW_PADDING

        # create buffer
        buffer = io.BytesIO()

        # save PNG in buffer
        image.save(buffer, format='PNG')    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)
        
        return discord.File(buffer, 'myimage.png')
    
    @commands.group()
    async def hg(self, ctx):
        """
        Hunger Games using !hg <action>, choosing from below...
        """

        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 6):
            raise commands.BadArgument(
                "You need to be an Administrator or higher to use that command.")

        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid giveaway subcommand passed. Options: `start`, `reroll`, `end`")

    
    @hg.command(name="new")
    @commands.guild_only()
    async def new(self, ctx, *, title: str = None):
        """
        Start a new Hunger Games simulation in the current channel.
        Each channel can only have one simulation running at a time.

        title - (Optional) The title of the simulation. Defaults to 'The Hunger Games'
        """
        title = "The Hunger Games"
        owner = ctx.author
        ret = self.game_instance.new_game(ctx.channel.id, owner.id, owner.name, title)
        if not await self.__check_errors(ctx, ret):
            return
        await ctx.send(embed=discord.Embed(description=f"{owner.mention} has started {title}! Type `!hg join` to enter the "
                    "game yourself! Admins can use `!hg add <@user>` to add someone.", color=discord.Color.random()))


    @hg.command(name="join")
    @commands.guild_only()
    async def join(self, ctx):
        """
        Adds a tribute with your name to a new simulation.
        """
        name = ctx.author.display_name
        ret = self.game_instance.add_player(ctx.channel.id, name, ctx.author.id, volunteer=True)
        if not await self.__check_errors(ctx, ret):
            return
        await ctx.reply(ret)


    @hg.command(name="add")
    @commands.guild_only()
    async def add(self, ctx, *, member: discord.Member):
        """
        Add a user to a new game.

        name - The name of the tribute to add. Limit 32 chars. Leading and trailing whitespace will be trimmed.
        Special chars @*_`~ count for two characters each.
        """
        ret = self.game_instance.add_player(ctx.channel.id, member.display_name, member.id)
        if not await self.__check_errors(ctx, ret):
            return
        await ctx.send(ret)


    @hg.command(name="remove")
    @commands.guild_only()
    async def remove(self, ctx, member: discord.Member):
        """
        Remove a user from a new game.
        Only the game's host may use this command.

        name - The name of the tribute to remove.
        """

        ret = self.game_instance.remove_player(ctx.channel.id, member.id)
        if not await self.__check_errors(ctx, ret):
            return
        await ctx.send(ret)


    @hg.command(name="fill")
    @commands.guild_only()
    async def fill(self, ctx):
        """Fill empty slots with random people
        """

        ret = self.game_instance.pad_players(ctx.channel.id, list(ctx.message.guild.members))
        if not await self.__check_errors(ctx, ret):
            return
        await ctx.send(ret)


    @hg.command(name="status")
    @commands.guild_only()
    async def status(self, ctx):
        """
        Gets the status for the game in the channel.
        """
        ret = self.game_instance.status(ctx.channel.id)
        if len(ret) == 0:
            if not await self.__check_errors(ctx, ret):
                return
        ret, players = ret
        if len(players) == 0:
            embed = discord.Embed(title=ret['title'], description=ret['description'])
            embed.set_footer(text=ret['footer'])
            await ctx.reply(embed=embed)
        else:
            await ctx.reply(file=await self.produce_leaderboard_image(ctx, ret['title'], players))

    @hg.command(name="start")
    @commands.guild_only()
    async def start(self, ctx, autoplay=False):
        """
        Starts the pending game in the channel.
        """
        ret = self.game_instance.start_game(ctx.channel.id, ctx.author.id)
        if not await self.__check_errors(ctx, ret):
            return
        ret, players = ret
        embed = discord.Embed(title=ret['title'], description=ret['description'])
        embed.set_footer(text=ret['footer'])
        embed.color = discord.Color.random()
        await ctx.reply(embed=embed, file=await self.produce_leaderboard_image(ctx, ret['title'], players))
        
        if autoplay:
            self.game_instance.autoplay = True
            while not await self.step(ctx):
                await asyncio.sleep(20)


    @hg.command(name="end")
    @commands.guild_only()
    async def end(self, ctx):
        """
        Cancels the current game in the channel.
        """
        ret = self.game_instance.end_game(ctx.channel.id, ctx.author.id)
        if not await self.__check_errors(ctx, ret):
            return
        await ctx.send("{0} has been cancelled. Anyone may now start a new game with `{1}new`.".format(ret.title, "!"))


    @hg.command(name="step")
    @commands.guild_only()
    async def step(self, ctx):
        """
        Steps forward the current game in the channel by one round.
        """
        ret = self.game_instance.step(ctx.channel.id, ctx.author.id)
        if not await self.__check_errors(ctx, ret):
            return True

        if ret.get('members') is not None:
            title = ret.get('title')
            lines = []
            for message, member in zip(ret['messages'], ret['members']):
                lines.append({'message': message, 'members': member})

            lines_grouped = list(self.grouper(4, lines))
            max_width = 0
            for lines in lines_grouped:
                for line in lines:
                    if line is not None:
                        if len(line["members"]) > max_width:
                            max_width = len(line["members"])
        
            async with ctx.typing():            
                first = True
                for lines in lines_grouped:
                    if not first:
                        await asyncio.sleep(10)
                    first = False
                    await ctx.send(file=await self.produce_image(ctx, title, lines, max_width))
                
                if ret.get('description(') is not None:
                    await asyncio.sleep(2)
                    embed = discord.Embed(color=ret['color'], description=ret['description'])
                    if ret['footer'] is not None:
                        embed.set_footer(text=ret['footer'])
                    await ctx.send(embed=embed)
                else:
                    await asyncio.sleep(2)
                    embed = discord.Embed(color=ret['color'], description="Proceed.")
                    if self.game_instance.autoplay:
                        embed.set_footer(text="The next round commences in 20 seconds.")
                    else:
                        embed.set_footer(text="Use command `!hg step`.")
                    await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=ret['title'], color=ret['color'], description=ret['description'])
            if ret['footer'] is not None:
                embed.set_footer(text=ret['footer'])
            await ctx.send(embed=embed)

        return False

    def grouper(self, n, iterable, fillvalue=None):
        args = [iter(iterable)] * n
        return itertools.zip_longest(*args, fillvalue=fillvalue)

    async def __check_errors(self, ctx, error_code):
        if type(error_code) is not ErrorCode:
            return True
        if error_code is ErrorCode.NO_GAME:
            raise commands.BadArgument("There is no game currently running in this channel.")
            return False
        if error_code is ErrorCode.GAME_EXISTS:
            raise commands.BadArgument("A game has already been started in this channel.")
            return False
        if error_code is ErrorCode.GAME_STARTED:
            raise commands.BadArgument("This game is already running.")
            return False
        if error_code is ErrorCode.GAME_FULL:
            raise commands.BadArgument("This game is already at maximum capacity.")
            return False
        if error_code is ErrorCode.PLAYER_EXISTS:
            raise commands.BadArgument("That person is already in this game.")
            return False
        if error_code is ErrorCode.CHAR_LIMIT:
            raise commands.BadArgument("That name is too long (max 32 chars).")
            return False
        if error_code is ErrorCode.NOT_OWNER:
            raise commands.BadArgument("You are not the owner of this game.")
            return False
        if error_code is ErrorCode.INVALID_GROUP:
            raise commands.BadArgument("That is not a valid group. Valid groups are:\n```\n{0}\n```"
                            .format("\n".join(list(default_players.keys()))))
            return False
        if error_code is ErrorCode.NOT_ENOUGH_PLAYERS:
            raise commands.BadArgument("There are not enough players to start a game. There must be at least 2.")
            return False
        if error_code is ErrorCode.GAME_NOT_STARTED:
            raise commands.BadArgument("This game hasn't been started yet.")
            return False
        if error_code is ErrorCode.PLAYER_DOES_NOT_EXIST:
            raise commands.BadArgument("There is no player with that name in this game.")
            return False

    @start.error
    @step.error
    @end.error
    @status.error
    @fill.error
    @add.error
    @join.error
    @new.error
    async def info_error(self, ctx, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.CommandOnCooldown)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            await self.bot.send_error(ctx, "A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(HungerGamesCog(bot))
