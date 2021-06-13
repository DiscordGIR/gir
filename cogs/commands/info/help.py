import traceback

import discord
from discord.ext import commands
import cogs.utils.permission_checks as permissions
import cogs.utils.context as context


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.left_col_length = 17
        self.right_col_length = 80
        self.mod_only = ["ModActions", "ModUtils", "Filters", "BoosterEmojis", "ReactionRoles", "Giveaway", "Admin", "AntiRaid"]
        self.genius_only = ["Genius"]

    @commands.command(name="help", hidden=True)
    @commands.guild_only()
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def help_comm(self, ctx: context.Context, *, command_arg: str = None):
        """Gets all cogs and commands of mine."""

        await ctx.message.delete(delay=5)

        if not command_arg:
            await ctx.message.add_reaction("📬")
            header = "Get a detailed description for a specific command with `!help <command name>`\n"
            string = ""
            for cog_name in self.bot.cogs:
                cog = self.bot.cogs[cog_name]
                is_admin = ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 6)
                is_mod = ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 5)
                is_genius = ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 4)
                submod = ctx.guild.get_role(ctx.settings.guild().role_sub_mod)
                
                if not cog.get_commands() or (cog_name in self.mod_only and not is_mod):
                    continue
                elif not cog.get_commands() or (cog_name in self.genius_only and not is_genius):
                    continue
                elif cog_name == "SubNews" and not (submod in ctx.author.roles or is_admin):
                    continue
                
                string += f"== {cog_name} ==\n"

                for command in cog.get_commands():
                    # print(type(command), command)
                    spaces_left = ' ' * (self.left_col_length - len(command.name))
                    if command.help is not None:
                        command.brief = command.help.split("\n")[0]
                    else:
                        command.brief = "No description."
                    cmd_desc = command.brief[0:self.right_col_length] + "..." if len(command.brief) > self.right_col_length else command.brief

                    if isinstance(command, commands.core.Group):
                        string += f"\t* {command.name}{spaces_left} :: {cmd_desc}\n"
                        for c in command.commands:
                            spaces_left = ' ' * (self.left_col_length - len(c.name)-4)
                            if c.help is not None:
                                c.brief = c.help.split("\n")[0]
                            else:
                                c.brief = "No description."
                            cmd_desc = c.brief[0:self.right_col_length] + "..." if len(c.brief) > self.right_col_length else c.brief
                            string += f"\t\t* {c.name}{spaces_left} :: {cmd_desc}\n"
                    else:
                        string += f"\t* {command.name}{spaces_left} :: {cmd_desc}\n"

                string += "\n"

            try:
                parts = string.split("\n")
                group_size = 25
                if len(parts) <= group_size:
                    await ctx.author.send(header + "\n```asciidoc\n" + "\n".join(parts[0:group_size]) + "```")
                else:
                    seen = 0
                    await ctx.author.send(header + "\n```asciidoc\n" + "\n".join(parts[seen:seen+group_size]) + "```")
                    seen += group_size
                    while seen < len(parts):
                        await ctx.author.send("```asciidoc\n" + "\n".join(parts[seen:seen+group_size]) + "```")
                        seen += group_size
                        
            except Exception:
                raise commands.BadArgument("I tried to DM you but couldn't. Make sure your DMs are enabled.")

        else:
            command = self.bot.get_command(command_arg.lower())
            if command:
                # print(str(command.cog))
                if command.cog.qualified_name in self.mod_only and not ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
                    raise commands.BadArgument("You don't have permission to view that command.")
                elif command.cog.qualified_name in self.genius_only and not ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 4):
                    raise commands.BadArgument("You don't have permission to view that command.")
                else:
                    await ctx.message.add_reaction("📬")
                    embed = await self.get_usage_embed(ctx, command)
                    try:
                        await ctx.author.send(embed=embed)
                    except Exception:
                        raise commands.BadArgument("I tried to DM you but couldn't. Make sure your DMs are enabled.")
            else:
                raise commands.BadArgument("Command not found.", delete_after=5)

    @commands.command(name="usage", hidden=True)
    @commands.guild_only()
    @permissions.bot_channel_only_unless_mod()
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def usage(self, ctx: context.Context, *, command_arg: str):
        """Show usage of one command

        Parameters
        ----------
        command_arg : str
            Name of command
        """
        
        await ctx.message.delete(delay=5)
        command = self.bot.get_command(command_arg.lower())
        if command:
            embed = await self.get_usage_embed(ctx, command)
            await ctx.send(embed=embed)
        else:
            raise commands.BadArgument("Command not found.", delete_after=5)

    async def get_usage_embed(self,  ctx: context.Context, command):
        if command.cog.qualified_name in self.mod_only and not ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
            raise commands.BadArgument("You don't have permission to view that command.")
        elif command.cog.qualified_name in self.genius_only and not ctx.permissions.hasAtLeast(ctx.guild, ctx.author, 4):
            raise commands.BadArgument("You don't have permission to view that command.")
        else:
            args = ""
            for thing in command.clean_params:
                args += f"<{str(thing)}> "

            if command.full_parent_name:
                embed = discord.Embed(title=f"!{command.full_parent_name} {command.name} {args}")
            else:
                embed = discord.Embed(title=f"!{command.name} {args}")
            parts = command.help.split("\n\n")
            embed.description = parts[0] + '\n\n'
            for part in parts[1:len(parts)]:
                embed.description += "```\n"
                embed.description += part
                embed.description += "\n```"
            embed.color = discord.Color.random()
            return embed

    @usage.error
    @help_comm.error
    async def info_error(self,  ctx: context.Context, error):
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, permissions.PermissionsFailure)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await ctx.send_error(error)
        else:
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Utilities(bot))
