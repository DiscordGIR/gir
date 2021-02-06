import discord
from discord.ext import commands
import traceback
import io
from PIL import Image, ImageDraw, ImageFont

from cogs.commands.hungergames.default_players import default_players
from cogs.commands.hungergames.hungergames import HungerGames
from cogs.commands.hungergames.enums import ErrorCode

class HungerGamesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hg = HungerGames()
    
    @commands.command(name="test")
    @commands.guild_only()
    async def test(self, ctx):
        title = "Night 1"
        lines = [
            {
                "members": [777282444931104769, 109705860275539968, 109705860275539968, 145702927099494400, 193493980611215360],
                "message": "xd killed xd xd "
            },
            {
                "members": [777282444931104769, 109705860275539968, 145702927099494400, 193493980611215360],
                "message": "xd killed xd xd "
            },
            {
                "members": [777282444931104769, 109705860275539968, 145702927099494400],
                "message": "xd killed xd xd "
            },
            {
                "members": [516962733497778176, 747897273777782914],
                "message": "xd killed xd xd "
            },
            {
                "members": [275370518008299532],
                "message": "xd killed xd xd "
            },
            {
                "members": [516962733497778176, 747897273777782914],
                "message": "xd killed xd xd "
            },
            {
                "members": [275370518008299532],
                "message": "xd killed xd xd "
            },
        ]
        
        await ctx.send(file=await self.produce_image(ctx, title, lines))

    async def produce_image(self, ctx, title, lines):
        max_width = 0
        for line in lines:
            if len(line["members"]) > max_width:
                max_width = len(line["members"])
        
        
        UPPER_PADDING = 50
        LOWER_PADDING = 100
        
        ROW_HEIGHT = 160
        ROW_PADDING = 30
        IMAGE_WIDTH = 100 + (max_width * 150) + 100
        IMAGE_HEIGHT = UPPER_PADDING + (ROW_HEIGHT+ROW_PADDING)*len(lines) + LOWER_PADDING

        image = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT)) # RGB, RGBA (with alpha), L (grayscale), 1 (black & white)

        # create object for drawing
        draw = ImageDraw.Draw(image)
        # draw red rectangle with green outline from point (50,50) to point (550,250) #(600-50, 300-50)
        # draw.rectangle([50, 50, IMAGE_WIDTH-50, IMAGE_HEIGHT-50], fill=(255,0,0), outline=(0,255,0))

        # draw text in center
        current_y = 24
        text = line["message"]
        title_font = ImageFont.truetype('Arial.ttf', 36)
        text_width, text_height = draw.textsize(text, font=title_font)
        x = (IMAGE_WIDTH - text_width)//2 + 50
        draw.text( (x, current_y), title, fill=(255,255,255), font=title_font)
        
        
        current_y += ROW_PADDING + 50
        
        font = ImageFont.truetype('Arial.ttf', 24)
        
        for line in lines:
            # num_col = IMAGE_WIDTH // len(line["members"])
            offset = (max_width - (len(line["members"]))) * 75
            for i, member in enumerate(line["members"]):
                col_width = 150
                current_x = offset + (i * col_width ) + 100
                user = ctx.guild.get_member(member)
                pfp = user.avatar_url_as(format="png", size=128)
                pfp = Image.open(io.BytesIO(await pfp.read()))
                image.paste(pfp, (current_x, current_y))
                
                text = line["message"]
                text_width, text_height = draw.textsize(text, font=font)
                
                x = (IMAGE_WIDTH - text_width)//2
                y = current_y + 140
                draw.text( (x, y), text, fill=(255,255,255), font=font)
            current_y += ROW_HEIGHT + ROW_PADDING

        # create buffer
        buffer = io.BytesIO()

        # save PNG in buffer
        image.save(buffer, format='PNG')    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)
        
        return discord.File(buffer, 'myimage.png')
    
    @commands.command(name="new")
    @commands.guild_only()
    async def new(self, ctx, *, title: str = None):
        """
        Start a new Hunger Games simulation in the current channel.
        Each channel can only have one simulation running at a time.

        title - (Optional) The title of the simulation. Defaults to 'The Hunger Games'
        """
        title = "The Hunger Games"
        owner = ctx.author
        ret = self.hg.new_game(ctx.channel.id, owner.id, owner.name, title)
        if not await self.__check_errors(ctx, ret):
            return
        await ctx.send(f"{owner.mention} has started {title}! Use `!add [-m|-f] <name>` to add a player or `!join [-m|-f]` to enter the "
                    "game yourself!")


    @commands.command(name="join")
    @commands.guild_only()
    async def join(self, ctx, gender=None):
        """
        Adds a tribute with your name to a new simulation.

        gender (Optional) - Use `-m` or `-f` to set male or female gender. Defaults to a random gender.
        """
        name = ctx.author.nick if ctx.author.nick is not None else ctx.author.name
        ret = self.hg.add_player(ctx.channel.id, name, gender=gender, volunteer=True)
        if not await self.__check_errors(ctx, ret):
            return
        await ctx.reply(ret)


    @commands.command(name="add")
    @commands.guild_only()
    async def add(self, ctx, *, name: str):
        """
        Add a user to a new game.

        name - The name of the tribute to add. Limit 32 chars. Leading and trailing whitespace will be trimmed.
        Special chars @*_`~ count for two characters each.
        \tPrepend the name with a `-m ` or `-f ` flag to set male or female gender. Defaults to a random gender.
        """
        ret = self.hg.add_player(ctx.channel.id, name)
        if not await self.__check_errors(ctx, ret):
            return
        await ctx.send(ret)


    @commands.command(name="remove")
    @commands.guild_only()
    async def remove(self, ctx, *, name: str):
        """
        Remove a user from a new game.
        Only the game's host may use this command.

        name - The name of the tribute to remove.
        """

        ret = self.hg.remove_player(ctx.channel.id, name)
        if not await self.__check_errors(ctx, ret):
            return
        await ctx.send(ret)


    @commands.command(name="fill")
    @commands.guild_only()
    async def fill(self, ctx, group_name=None):
        """
        Pad out empty slots in a new game with default characters.

        group_name (Optional) - The builtin group to draw tributes from. Defaults to members in this guild.
        """
        if group_name is None:
            group = []
            for m in list(ctx.message.guild.members):
                if m.nick is not None:
                    group.append(m.nick)
                else:
                    group.append(m.name)
        else:
            group = default_players.get(group_name)

        ret = self.hg.pad_players(ctx.channel.id, group)
        if not await self.__check_errors(ctx, ret):
            return
        await ctx.send(ret)


    @commands.command(name="status")
    @commands.guild_only()
    async def status(self, ctx):
        """
        Gets the status for the game in the channel.
        """
        ret = self.hg.status(ctx.channel.id)
        if not await self.__check_errors(ctx, ret):
            return
        embed = discord.Embed(title=ret['title'], description=ret['description'])
        embed.set_footer(text=ret['footer'])
        await ctx.send(embed=embed)


    @commands.command(name="start")
    @commands.guild_only()
    async def start(self, ctx):
        """
        Starts the pending game in the channel.
        """
        ret = self.hg.start_game(ctx.channel.id, ctx.author.id, "!")
        if not await self.__check_errors(ctx, ret):
            return
        embed = discord.Embed(title=ret['title'], description=ret['description'])
        embed.set_footer(text=ret['footer'])
        await ctx.send(embed=embed)


    @commands.command(name="end")
    @commands.guild_only()
    async def end(self, ctx):
        """
        Cancels the current game in the channel.
        """
        ret = self.hg.end_game(ctx.channel.id, ctx.author.id)
        if not await self.__check_errors(ctx, ret):
            return
        await ctx.send("{0} has been cancelled. Anyone may now start a new game with `{1}new`.".format(ret.title, "!"))


    @commands.command(name="step")
    @commands.guild_only()
    async def step(self, ctx):
        """
        Steps forward the current game in the channel by one round.
        """
        ret = self.hg.step(ctx.channel.id, ctx.author.id)
        if not await self.__check_errors(ctx, ret):
            return
        embed = discord.Embed(title=ret['title'], color=ret['color'], description=ret['description'])
        if ret['footer'] is not None:
            embed.set_footer(text=ret['footer'])
        await ctx.send(embed=embed)


    async def __check_errors(self, ctx, error_code):
        if type(error_code) is not ErrorCode:
            return True
        if error_code is ErrorCode.NO_GAME:
            await ctx.reply("There is no game currently running in this channel.")
            return False
        if error_code is ErrorCode.GAME_EXISTS:
            await ctx.reply("A game has already been started in this channel.")
            return False
        if error_code is ErrorCode.GAME_STARTED:
            await ctx.reply("This game is already running.")
            return False
        if error_code is ErrorCode.GAME_FULL:
            await ctx.reply("This game is already at maximum capacity.")
            return False
        if error_code is ErrorCode.PLAYER_EXISTS:
            await ctx.reply("That person is already in this game.")
            return False
        if error_code is ErrorCode.CHAR_LIMIT:
            await ctx.reply("That name is too long (max 32 chars).")
            return False
        if error_code is ErrorCode.NOT_OWNER:
            await ctx.reply("You are not the owner of this game.")
            return False
        if error_code is ErrorCode.INVALID_GROUP:
            await ctx.reply("That is not a valid group. Valid groups are:\n```\n{0}\n```"
                            .format("\n".join(list(default_players.keys()))))
            return False
        if error_code is ErrorCode.NOT_ENOUGH_PLAYERS:
            await ctx.reply("There are not enough players to start a game. There must be at least 2.")
            return False
        if error_code is ErrorCode.GAME_NOT_STARTED:
            await ctx.reply("This game hasn't been started yet.")
            return False
        if error_code is ErrorCode.PLAYER_DOES_NOT_EXIST:
            await ctx.reply("There is no player with that name in this game.")
            return False

    @test.error
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
