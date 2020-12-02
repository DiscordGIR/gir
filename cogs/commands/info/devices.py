import discord
from discord.ext import commands
import traceback
import aiohttp
import json
import re

class Devices(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.devices_url = "https://api.ipsw.me/v4/devices"
        self.firmwares_url = "https://api.ipsw.me/v4/device/"
        self.devices_test = re.compile(r'^.+ \[.+\,.+\]$')
        self.possible_devices = ['iphone', 'ipod', 'ipad', 'homepod', 'apple']

    @commands.guild_only()
    @commands.command(name="adddevice")
    async def adddevice(self, ctx: commands.Context, *, device: str) -> None:
        """Add device name to your nickname, i.e `SlimShadyIAm [iPhone 12, 14.2]`. See !listdevices to see the list of possible devices.
        
        Example usage:
        `!adddevice <device name>`

        Parameters
        ----------
        device : str
            device user wants to use

        """

        bot_chan = self.bot.settings.guild().channel_botspam
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and ctx.channel.id != bot_chan:
            await ctx.message.delete()
            raise commands.BadArgument(f"Command only allowed in <#{bot_chan}>")

        
        if re.match(self.devices_test, ctx.author.display_name):
            await ctx.message.delete()
            raise commands.BadArgument("You already have a device nickname set!")

        the_device = None

        async with aiohttp.ClientSession() as session:
            async with session.get(self.devices_url) as resp:
                if resp.status == 200:
                    data = await resp.text()
                    devices = json.loads(data)
                    # devices.append({'name': 'Apple Watch Series 6', 'identifier': 'Watch6,4'})
                    # devices.append({'name': 'Apple Watch SE', 'identifier': 'Watch5,12'})
                    devices.append({'name': 'iPhone SE 2', 'identifier': 'iPhone12,8'})
                    for d in devices:
                        # if "Apple Watch" in d["name"]:
                        # print(d["name"])
                        name = re.sub(r'\((.*?)\)', "", d["name"])
                        name = name.replace('[', '')
                        name = name.replace(']', '')
                        if name.lower() == device.lower():
                            the_device = d

        

        if not the_device:
            await ctx.message.delete()
            raise commands.BadArgument("Device doesn't exist!")

        if not the_device["name"].split(" ")[0].lower() in self.possible_devices:
            await ctx.message.delete()
            raise commands.BadArgument("Unsupported device. Please see `!listdevices` for possible devices.")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        firmwares = None
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.firmwares_url}/{the_device['identifier']}") as resp:
                if resp.status == 200:
                    firmwares = json.loads(await resp.text())["firmwares"]

        found = False
        firmware = None
        while True:
            prompt = await ctx.message.reply("Please enter a version number (or 'cancel' to cancel)")
            msg = await self.bot.wait_for('message', check=check)

            if msg.content.lower() == "cancel":
                await prompt.delete()
                return

            for f in firmwares:
                if f["version"] == msg.content:
                    found = True
                    firmware = f["version"]
                    break

            await prompt.delete()
            await msg.delete()
            
            if found:
                break
        
        if found and firmware:
            name = the_device["name"]
            name.replace(' Plus', '+')
            name.replace('Pro Max', 'PM')
            new_nick = f"{ctx.author.display_name} [{name}, {firmware}]"
            if len(new_nick) > 32:
                await ctx.message.delete()
                raise commands.BadArgument("Nickname too long! Aborting.")
            await ctx.author.edit(nick=new_nick)
            await ctx.message.reply("Changed your nickname!")
        else:
            raise commands.BadArgument("An error occured :(")

    @commands.guild_only()
    @commands.command(name="removedevice")
    async def removedevice(self, ctx: commands.Context) -> None:
        """Removes device from your nickname
        
        Example usage:
        `!removedevice`

        """
        
        bot_chan = self.bot.settings.guild().channel_botspam
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and ctx.channel.id != bot_chan:
            await ctx.message.delete()
            raise commands.BadArgument(f"Command only allowed in <#{bot_chan}>")
        
        if not re.match(self.devices_test, ctx.author.display_name):
            await ctx.message.delete()
            raise commands.BadArgument("You don't have a device nickname set!")

        new_nick = re.sub(self.devices_test, "", ctx.author.display_name)
        if len(new_nick) > 32:
            await ctx.message.delete()
            raise commands.BadArgument("Nickname too long")

        await ctx.author.edit(nick=new_nick)
        await ctx.message.reply("Removed device from your nickname!")
        
    @commands.guild_only()
    @commands.command(name="listdevices")
    async def listdevices(self, ctx) -> None:
        """List all possible devices you can set your nickname to.

        Example usage:
        `!listdevices`

        """

        bot_chan = self.bot.settings.guild().channel_botspam
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and ctx.channel.id != bot_chan:
            await ctx.message.delete()
            raise commands.BadArgument(f"Command only allowed in <#{bot_chan}>")
        
        devices_dict = {
            'iPhone': set(),
            'iPod': set(),
            'iPad': set(),
            'Apple TV': set(),
            'Apple Watch': set(),
            'HomePod': set(),
        }    

        async with aiohttp.ClientSession() as session:
            async with session.get(self.devices_url) as resp:
                if resp.status == 200:
                    data = await resp.text()
                    devices = json.loads(data)
                    for d in devices:
                        name = re.sub(r'\((.*?)\)', "", d["name"])
                        name = name.replace('[', '')
                        name = name.replace(']', '')
                        name = name.strip()
                        for key in devices_dict.keys():
                            if key in name:
                                devices_dict[key].add(name)

        devices_dict["iPhone"].add("iPhone SE 2")
        devices_dict["Apple Watch"].add("Apple Watch Series 6")
        devices_dict["Apple Watch"].add("Apple Watch SE")

        embed=discord.Embed(title="Devices list")
        embed.color=discord.Color.blurple()
        for key in devices_dict.keys():
            temp = list(devices_dict[key])
            temp.sort()
            embed.add_field(name=key, value=', '.join(map(str, temp)), inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author}")
        
        await ctx.message.reply(embed=embed)

    @removedevice.error
    @adddevice.error
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
    bot.add_cog(Devices(bot))
