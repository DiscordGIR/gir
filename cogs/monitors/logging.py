import discord
from discord.ext import commands
from datetime import datetime
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

        

def setup(bot):
    bot.add_cog(Logging(bot))