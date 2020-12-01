import discord
from discord.ext import commands
from datetime import datetime
from io import BytesIO
# logging
# nsa

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.nsa_guild_id = 783116252842819604
        self.channel_map = {
            777886186655055903: 783116252842819608, #general
            777270542033092638: 783116711024394290, #public
            777270554800422943: 783116725021442048, #private
            777270579719569410: 783116739205398558, #report
            778233669881561088: 783116754183520268, #bot-commands
            779762542704722040: 783116763919286303, #todo
            782765012510965781: 783116773460279316, #ignore-1
            782765029735923722: 783116783929786429, #ignore-2
        }

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != self.bot.settings.guild_id:
            return
        
        channel = discord.utils.get(member.guild.channels, id=self.bot.settings.guild().channel_private)

        embed=discord.Embed(title="Member joined")
        embed.color=discord.Color.green()
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="User", value=f'{member} ({member.mention})', inline=True)
        embed.add_field(name="Warnpoints", value=(await self.bot.settings.user(member.id)).warn_points, inline=True)
        embed.add_field(name="Joined", value=member.joined_at.strftime("%B %d, %Y, %I:%M %p") + " UTC", inline=False)
        embed.add_field(name="Created", value=member.created_at.strftime("%B %d, %Y, %I:%M %p") + " UTC", inline=True)
        embed.set_footer(text=member.id)
        await channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id != self.bot.settings.guild_id:
            return
        
        channel = discord.utils.get(member.guild.channels, id=self.bot.settings.guild().channel_private)

        embed=discord.Embed(title="Member left")
        embed.color=discord.Color.purple()
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="User", value=f'{member} ({member.mention})', inline=True)
        embed.set_footer(text=member.id)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.guild:
            return
        if before.guild.id != self.bot.settings.guild_id:
            return
        if before.content == after.content:
            return

        channel = discord.utils.get(before.guild.channels, id=self.bot.settings.guild().channel_private)

        embed=discord.Embed(title="Message Updated")
        embed.color=discord.Color.purple()
        embed.set_thumbnail(url=before.author.avatar_url)
        embed.add_field(name="User", value=f'{before.author} ({before.author.mention})', inline=False)
        embed.add_field(name="Old message", value=before.content, inline=False)
        embed.add_field(name="New message", value=before.content, inline=False)
        embed.add_field(name="Channel", value=before.channel.mention, inline=False)
        embed.set_footer(text=before.author.id)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild:
            return
        if message.guild.id != self.bot.settings.guild_id:
            return
        
        if message.author.bot:
            return
        if message.content == "" or not message.content:
            return
            
        channel = discord.utils.get(message.guild.channels, id=self.bot.settings.guild().channel_private)
       
        embed=discord.Embed(title="Message Deleted")
        embed.color=discord.Color.red()
        embed.set_thumbnail(url=message.author.avatar_url)
        embed.add_field(name="User", value=f'{message.author} ({message.author.mention})', inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="Message", value=message.content, inline=False)
        embed.set_footer(text=message.author.id)
        embed.timestamp = datetime.now()
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        if not messages[0].guild:
            return
        if messages[0].guild.id != self.bot.settings.guild_id:
            return
        members = set()
        channel = discord.utils.get(messages[0].guild.channels, id=self.bot.settings.guild().channel_private)
        output = BytesIO()
        for message in messages:
            members.add(message.author)

            string = f'{message.author} ({message.author.id}) [{message.created_at.strftime("%B %d, %Y, %I:%M %p")}]) UTC\n'
            string += message.content
            for attachment in message.attachments:
                string += f'\n{attachment.url}'

            string += "\n\n"
            output.write(string.encode('UTF-8'))
        output.seek(0)

        member_string = ""
        for i, member in enumerate(members):
            if i == len(members) -1 and i == 0:
                member_string += f"{member.mention}"
            elif i == len(members) -1 and i != 0:
                member_string += f"and {member.mention}"
            else:
                member_string += f"{member.mention}, "

        embed=discord.Embed(title="Bulk Message Deleted")
        embed.color=discord.Color.red()
        embed.add_field(name="Users", value=f'This batch included {len(messages)} messages from {member_string}', inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        await channel.send(embed=embed)
        await channel.send(file=discord.File(output, 'message.txt'))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild.id != self.bot.settings.guild_id:
            return

        nsa = self.bot.get_guild(id=self.nsa_guild_id)
        channel = discord.utils.get(nsa.channels, id=self.channel_map[message.channel.id])

        embed=discord.Embed()
        embed.color = message.author.color
        embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
        embed.add_field(name="Body", value=message.content if message.content else "Message has no body.", inline=False)
        embed.add_field(name="Message ID", value=message.id, inline=False)
        embed.add_field(name="Message link", value=f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}", inline=False)
        embed.set_footer(text="User ID: " + str(message.author.id))
        embed.timestamp = message.created_at

        log = await channel.send(embed=embed)
        for embed in message.embeds:
            await log.reply("Message contained embed", embed=embed)
        for attachment in message.attachments:
            await log.reply(file=(await attachment.to_file()))

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
    bot.add_cog(Logging(bot))