import traceback

import discord
from discord.ext import commands


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.left_col_length = 17
        self.right_col_length = 80
        self.mod_only = ["ModActions", "Filters", "BoosterEmojis"]
        self.genius_only = ["Genius"]

    @commands.command(name="help", hidden=True)
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def help_comm(self, ctx: commands.Context, command_arg: str = None):
        """Gets all cogs and commands of mine."""

        await ctx.message.delete(delay=5)

        if not command_arg:
            await ctx.message.add_reaction("📬")
            header = "Get a detailed description for a specific command with `!help <command name>`\n"
            string = ""
            for cog_name in self.bot.cogs:
                cog = self.bot.cogs[cog_name]
                if not cog.get_commands() or (cog_name in self.mod_only and not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5)):
                    continue
                elif not cog.get_commands() or (cog_name in self.genius_only and not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 4)):
                    continue

                string += f"# {cog_name}\n"

                for command in cog.get_commands():
                    spaces_left = ' ' * (self.left_col_length - len(command.name))
                    command.brief = command.help.split("\n")[0]
                    cmd_desc = command.brief[0:self.right_col_length] + "..." if len(command.brief) > self.right_col_length else command.brief
                    string += f"\t- {command.name}{spaces_left}{cmd_desc}\n"

            try:
                parts = string.split("\n")
                group_size = 20
                if len(parts) <= group_size:
                    await ctx.author.send(header + "\n```md\n" + "\n".join(parts[0:group_size]) + "```")
                else:
                    seen = 0
                    await ctx.author.send(header + "\n```md\n" + "\n".join(parts[seen:seen+group_size]) + "```")
                    seen += group_size
                    while seen < len(parts):
                        await ctx.author.send("```md\n" + "\n".join(parts[seen:seen+group_size]) + "```")
                        seen += group_size
                        
            except Exception:
                await ctx.send("I tried to DM you but couldn't. Make sure your DMs are enabled.")

        else:
            command = self.bot.get_command(command_arg.lower())
            if command:
                # print(str(command.cog))
                if command.cog.qualified_name in self.mod_only and not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5):
                    raise commands.BadArgument("You don't have permission to view that command.")
                elif command.cog.qualified_name in self.genius_only and not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 4):
                    raise commands.BadArgument("You don't have permission to view that command.")
                else:
                    await ctx.message.add_reaction("📬")
                    string = f"Results for {command_arg.lower()} ```md\n"
                    
                    # prefix = self.bot.command_prefix()[0]
                    args = ""
                    for thing in command.clean_params:
                        args += f"<{str(thing)}> "
                    string += f"!{command.name} {args}\n\n{command.help}"
                    string += "\n```"
                    
                    try:
                        await ctx.author.send(string)
                    except Exception:
                        await ctx.send("I tried to DM you but couldn't. Make sure your DMs are enabled.")
            else:
                await ctx.send("Command not found.", delete_after=5)

    @help_comm.error
    async def info_error(self, ctx, error):
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Utilities(bot))
