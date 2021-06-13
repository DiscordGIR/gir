import aiohttp
import traceback
from io import BytesIO

import discord
from data.tag import Tag
import datetime
import cogs.utils.permission_checks as permissions
import cogs.utils.context as context
from discord.ext import commands
from discord.ext import menus


class TagsSource(menus.GroupByPageSource):
    async def format_page(self, menu, entry):
        embed = discord.Embed(
            title=f'All tags', color=discord.Color.blurple())
        for tag in entry.items:
            desc = f"Added by: {tag.added_by_tag}\nUsed {tag.use_count} times"
            if tag.image.read() is not None:
                desc += "\nHas image attachment"
            embed.add_field(name=tag.name, value=desc)
        embed.set_footer(
            text=f"Page {menu.current_page +1} of {self.get_max_pages()}")
        return embed


class MenuPages(menus.MenuPages):
    async def update(self, payload):
        if self._can_remove_reactions:
            if payload.event_type == 'REACTION_ADD':
                await self.message.remove_reaction(payload.emoji, payload.member)
            elif payload.event_type == 'REACTION_REMOVE':
                return
        await super().update(payload)

class CustomBucketType(commands.BucketType):
    custom = 7
    
    def get_key(self, tag):
        return tag
        
        
class CustomCooldown(commands.Cooldown):
    __slots__ = ('rate', 'per', 'type', '_window', '_tokens', '_last')

    def __init__(self, rate, per, type):
        self.rate = int(rate)
        self.per = float(per)
        self.type = type
        self._window = 0.0
        self._tokens = self.rate
        self._last = 0.0

        if not isinstance(self.type, CustomBucketType):
            raise TypeError('Cooldown type must be a BucketType')
        
    def copy(self):
        return CustomCooldown(self.rate, self.per, self.type)


class CustomCooldownMapping(commands.CooldownMapping):
    def __init__(self, original):
        self._cache = {}
        self._cooldown = original
        
    @classmethod
    def from_cooldown(cls, rate, per, type):
        return cls(CustomCooldown(rate, per, type))


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.tag_cooldown = CustomCooldownMapping.from_cooldown(1, 5, CustomBucketType.custom)

    @commands.guild_only()
    @permissions.genius_or_submod_and_up()
    @commands.command(name="addtag", aliases=['addt'])
    async def addtag(self, ctx: context.Context, name: str, *, content: str) -> None:
        """Add a tag. Optionally attach an iamge. (Genius only)

        Example usage:
        -------------
        `!addtag roblox This is the content`

        Parameters
        ----------
        name : str
            Name of the tag
        content : str
            Content of the tag
        """

        if not name.isalnum():
            raise commands.BadArgument("Tag name must be alphanumeric.")

        if (await ctx.settings.get_tag(name.lower())) is not None:
            raise commands.BadArgument("Tag with that name already exists.")

        tag = Tag()
        tag.name = name.lower()
        tag.content = content
        tag.added_by_id = ctx.author.id
        tag.added_by_tag = str(ctx.author)
        
        if len(ctx.message.attachments) > 0:
            image, _type = await self.do_content_parsing(ctx.message.attachments[0].url)
            if _type is None:
                raise commands.BadArgument("Attached file was not an image.")
            tag.image.put(image, content_type=_type)

        await ctx.settings.add_tag(tag)
        
        file = tag.image.read()
        if file is not None:
            file = discord.File(BytesIO(file), filename="image.gif" if tag.image.content_type == "image/gif" else "image.png")

        await ctx.message.reply(f"Added new tag!", file=file, embed=await self.tag_embed(tag), delete_after=10)
        await ctx.message.delete(delay=10)
    
    async def do_content_parsing(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as resp:
                if resp.status != 200:
                    return None, None
                elif resp.headers["CONTENT-TYPE"] not in ["image/png", "image/jpeg", "image/gif", "image/webp"]:
                    return None, None
                else:
                    async with session.get(url) as resp2:
                        if resp2.status != 200:
                            return None
                        return await resp2.read(), resp2.headers['CONTENT-TYPE']
                        
    async def tag_embed(self, tag):
        embed = discord.Embed(title=tag.name)
        embed.description = tag.content
        embed.timestamp = tag.added_date
        embed.color = discord.Color.blue()

        if tag.image.read() is not None:
            embed.set_image(url="attachment://image.gif" if tag.image.content_type == "image/gif" else "attachment://image.png")
        embed.set_footer(text=f"Added by {tag.added_by_tag} | Used {tag.use_count} times")
        return embed

    @commands.guild_only()
    @permissions.bot_channel_only_unless_mod()
    @commands.command(name="taglist", aliases=['tlist'])
    async def taglist(self, ctx: context.Context):
        """List all tags
        """

        tags = sorted(ctx.settings.guild().tags, key=lambda tag: tag.name)

        if len(tags) == 0:
            raise commands.BadArgument("There are no tags defined.")
        
        menus = MenuPages(source=TagsSource(
            tags, key=lambda t: 1, per_page=12), clear_reactions_after=True)

        await menus.start(ctx)

    @commands.guild_only()
    @permissions.genius_or_submod_and_up()
    @commands.command(name="deltag", aliases=['dtag'])
    async def deltag(self, ctx: context.Context, name: str):
        """Delete tag (geniuses only)

        Example usage:
        --------------
        `!deltag <tagname>`

        Parameters
        ----------
        name : str
            Name of tag to delete

        """

        name = name.lower()

        tag = await ctx.settings.get_tag(name)
        if tag is None:
            raise commands.BadArgument("That tag does not exist.")

        await ctx.settings.remove_tag(name)
        await ctx.send_warning("Deleted that tag.", delete_after=5)
        await ctx.message.delete(delay=5)

    @commands.guild_only()
    @commands.command(name="tag", aliases=['t'])
    async def tag(self, ctx: context.Context, name: str):
        """Use a tag with a given name.
        
        Example usage
        -------------
        !t roblox

        Parameters
        ----------
        name : str
            Name of tag to use
        """

        name = name.lower()
        tag = await ctx.settings.get_tag(name)
        
        if tag is None:
            raise commands.BadArgument("That tag does not exist.")
        if not (ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 5) or ctx.guild.get_role(ctx.settings.guild().role_sub_mod) in ctx.author.roles):
            bucket = self.tag_cooldown.get_bucket(tag.name)
            current = ctx.message.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()

            if bucket.update_rate_limit(current):
                raise commands.BadArgument("That tag is on cooldown.")

        file = tag.image.read()
        if file is not None:
            file = discord.File(BytesIO(file), filename="image.gif" if tag.image.content_type == "image/gif" else "image.png")
        
        await ctx.message.reply(embed=await self.tag_embed(tag), file=file, mention_author=False)
    
    @commands.guild_only()
    @permissions.genius_or_submod_and_up()
    @commands.command(name="edittag", aliases=['et'])
    async def edittag(self, ctx: context.Context, name: str, *, content: str) -> None:
        """Edit a tag's body.
        
        Example usage
        -------------
        !t roblox

        Parameters
        ----------
        name : str
            Name of tag to use
        """

        name = name.lower()
        tag = await ctx.settings.get_tag(name)
        
        if tag is None:
            raise commands.BadArgument("That tag does not exist.")
        
        tag.content = content
        if len(ctx.message.attachments) > 0:
            image, _type = await self.do_content_parsing(ctx.message.attachments[0].url)
            if _type is None:
                raise commands.BadArgument("Attached file was not an image.")
            tag.image.put(image, content_type=_type)
        else:
            tag.image = None

        if not await ctx.settings.edit_tag(tag):
            raise commands.BadArgument("An error occurred editing that tag.")
        
        file = tag.image.read()
        if file is not None:
            file = discord.File(BytesIO(file), filename="image.gif" if tag.image.content_type == "image/gif" else "image.png")
        
        await ctx.message.reply(embed=await self.tag_embed(tag), delete_after=10, file=file, mention_author=False)
        await ctx.message.delete(delay=10)

    @edittag.error
    @tag.error
    @taglist.error
    @deltag.error
    @addtag.error
    async def info_error(self, ctx: context.Context, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, permissions.PermissionsFailure)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await ctx.send_error(error)
        else:
            await ctx.send_error("A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Tags(bot))
