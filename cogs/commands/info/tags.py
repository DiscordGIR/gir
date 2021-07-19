import datetime
import traceback
from io import BytesIO

import aiohttp
import cogs.utils.context as context
import cogs.utils.permission_checks as permissions
import discord
from cogs.utils.message_cooldown import MessageTextBucket
from data.tag import Tag
from discord.ext import commands, menus
from discord.ext.commands.cooldowns import CooldownMapping


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


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tag_cooldown = CooldownMapping.from_cooldown(1, 5, MessageTextBucket.custom)

    @commands.guild_only()
    @permissions.genius_or_submod_and_up()
    @commands.command(name="addtag", aliases=['addt'])
    async def addtag(self, ctx: context.Context, name: str, *, content: str) -> None:
        """Add a tag. Optionally attach an iamge. (Genius only)

        Example usage
        -------------
        !addtag roblox This is the content

        Parameters
        ----------
        name : str
            "Name of the tag"
        content : str
            "Content of the tag"
        """

        if not name.isalnum():
            raise commands.BadArgument("Tag name must be alphanumeric.")

        if (await ctx.settings.get_tag(name.lower())) is not None:
            raise commands.BadArgument("Tag with that name already exists.")

        # prepare tag data for database
        tag = Tag()
        tag.name = name.lower()
        tag.content = content
        tag.added_by_id = ctx.author.id
        tag.added_by_tag = str(ctx.author)
        
        # did the user want to attach an image to this tag?
        if len(ctx.message.attachments) > 0:
            # ensure the attached file is an image
            image = ctx.message.attachments[0]
            _type = image.content_type
            if _type not in ["image/png", "image/jpeg", "image/gif", "image/webp"]:
                raise commands.BadArgument("Attached file was not an image.")
            else:
                image = await image.read()
            # save image bytes
            tag.image.put(image, content_type=_type)

        # store tag in database
        await ctx.settings.add_tag(tag)
        
        file = tag.image.read()
        if file is not None:
            file = discord.File(BytesIO(file), filename="image.gif" if tag.image.content_type == "image/gif" else "image.png")

        await ctx.message.reply(f"Added new tag!", file=file, embed=await self.prepare_tag_embed(tag), delete_after=10)
        await ctx.message.delete(delay=10)

    @commands.guild_only()
    @permissions.genius_or_submod_and_up()
    @commands.command(name="edittag", aliases=['et'])
    async def edittag(self, ctx: context.Context, name: str, *, content: str) -> None:
        """Edit a tag's body, optionally attach an image.
        
        Example usage
        -------------
        !edittag roblox this would be the body

        Parameters
        ----------
        name : str
            "Name of tag to edit"
        """

        name = name.lower()
        tag = await ctx.settings.get_tag(name)
        
        if tag is None:
            raise commands.BadArgument("That tag does not exist.")
        
        tag.content = content
        
        if len(ctx.message.attachments) > 0:
            # ensure the attached file is an image
            image = ctx.message.attachments[0]
            _type = image.content_type
            if _type not in ["image/png", "image/jpeg", "image/gif", "image/webp"]:
                raise commands.BadArgument("Attached file was not an image.")
            else:
                image = await image.read()
            
            # save image bytes
            if tag.image is not None:
                tag.image.replace(image, content_type=_type)
            else:
                tag.image.put(image, content_type=_type)
        else:
            tag.image = None

        if not await ctx.settings.edit_tag(tag):
            raise commands.BadArgument("An error occurred editing that tag.")
        
        file = tag.image.read()
        if file is not None:
            file = discord.File(BytesIO(file), filename="image.gif" if tag.image.content_type == "image/gif" else "image.png")
        
        await ctx.message.reply(embed=await self.prepare_tag_embed(tag), delete_after=10, file=file, mention_author=False)
        await ctx.message.delete(delay=10)

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
            "Name of tag to use"
        """

        name = name.lower()
        tag = await ctx.settings.get_tag(name)
        
        if tag is None:
            raise commands.BadArgument("That tag does not exist.")
        
        # run cooldown so tag can't be spammed
        bucket = self.tag_cooldown.get_bucket(tag.name)
        current = ctx.message.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()
        # ratelimit only if the invoker is not a moderator
        if bucket.update_rate_limit(current) and not (ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 5) or ctx.guild.get_role(ctx.settings.guild().role_sub_mod) in ctx.author.roles):
            raise commands.BadArgument("That tag is on cooldown.")
        
        # if the Tag has an image, add it to the embed
        file = tag.image.read()
        if file is not None:
            file = discord.File(BytesIO(file), filename="image.gif" if tag.image.content_type == "image/gif" else "image.png")
        
        await ctx.message.reply(embed=await self.prepare_tag_embed(tag), file=file, mention_author=False)

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

        Example usage
        --------------
        !deltag <tagname>

        Parameters
        ----------
        name : str
            "Name of tag to delete"

        """

        name = name.lower()

        tag = await ctx.settings.get_tag(name)
        if tag is None:
            raise commands.BadArgument("That tag does not exist.")

        await ctx.settings.remove_tag(name)
        await ctx.send_warning("Deleted that tag.", delete_after=5)
        await ctx.message.delete(delay=5)

    async def prepare_tag_embed(self, tag):
        """Given a tag object, prepare the appropriate embed for it

        Parameters
        ----------
        tag : Tag
            Tag object from database

        Returns
        -------
        discord.Embed
            The embed we want to send
        """
        embed = discord.Embed(title=tag.name)
        embed.description = tag.content
        embed.timestamp = tag.added_date
        embed.color = discord.Color.blue()

        if tag.image.read() is not None:
            embed.set_image(url="attachment://image.gif" if tag.image.content_type == "image/gif" else "attachment://image.png")
        embed.set_footer(text=f"Added by {tag.added_by_tag} | Used {tag.use_count} times")
        return embed

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
