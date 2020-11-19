import discord
from discord.ext import commands
from datetime import datetime
from io import BytesIO
# logging
# nsa

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != self.bot.settings.guild_id:
            return
        
        channel = discord.utils.get(member.guild.channels, id=self.bot.settings.channels.private)

        embed=discord.Embed(title="Member joined")
        embed.color=discord.Color.green()
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="User", value=f'{member} ({member.mention})', inline=True)
        embed.add_field(name="Warnpoints", value=123, inline=True)
        embed.add_field(name="Joined", value=member.joined_at.strftime("%B %d, %Y, %I:%M %p") + " UTC", inline=False)
        embed.add_field(name="Created", value=member.created_at.strftime("%B %d, %Y, %I:%M %p") + " UTC", inline=True)
        embed.set_footer(text=member.id)
        await channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id != self.bot.settings.guild_id:
            return
        
        channel = discord.utils.get(member.guild.channels, id=self.bot.settings.channels.private)

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
        channel = discord.utils.get(before.guild.channels, id=self.bot.settings.channels.private)

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

        channel = discord.utils.get(message.guild.channels, id=self.bot.settings.channels.private)
       
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
        channel = discord.utils.get(messages[0].guild.channels, id=self.bot.settings.channels.private)
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
        embed.add_field(name="Users", value=f'This batch included messages from {member_string}', inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        await channel.send(embed=embed)
        await channel.send(file=discord.File(output, 'message.txt'))

    @commands.command(name="purge")
    async def purge(self, ctx, limit:int):
        await ctx.channel.purge(limit=limit)
def setup(bot):
    bot.add_cog(Logging(bot))