import asyncio
import json
import re
import traceback

import aiohttp
import cogs.utils.context as context
import cogs.utils.permission_checks as permissions
import discord
from attr.setters import convert
from discord.ext import commands


class Confirm(discord.ui.View):
    def __init__(self, ctx: context.Context, true_response, false_response):
        super().__init__()
        self.ctx = ctx
        self.value = None
        self.true_response = true_response
        self.false_response = false_response


    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Yes', style=discord.ButtonStyle.success)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            await self.ctx.send_success(description=self.true_response, delete_after=5)
            self.value = True
            self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='No', style=discord.ButtonStyle.grey)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            await self.ctx.send_warning(description=self.false_response, delete_after=5)
            self.value = False
            self.stop()

class Devices(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.devices_url = "https://api.ipsw.me/v4/devices"
        self.firmwares_url = "https://api.ipsw.me/v4/device/"
        self.devices_test = re.compile(r'^.+ \[.+\,.+\]$')
        self.devices_remove_re = re.compile(r'\[.+\,.+\]$')
        self.possible_devices = ['iphone', 'ipod', 'ipad', 'homepod', 'apple']

    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.member, wait=False)
    @commands.bot_has_guild_permissions(change_nickname=True)
    @permissions.bot_channel_only_unless_mod()
    @permissions.ensure_invokee_role_lower_than_bot()
    @commands.command(name="adddevice", aliases=["addevice"])
    async def adddevice(self, ctx: context.Context, *, device: str) -> None:
        """Add device name to your nickname, i.e `SlimShadyIAm [iPhone 12, 14.2]`. See !listdevices to see the list of possible devices.

        Example usage
        -------------
        !adddevice <device name>

        Parameters
        ----------
        device : str
            "device user wants to use"

        """
        new_nick = ctx.author.display_name
        # check if user already has a device in their nick
        if re.match(self.devices_test, ctx.author.display_name):
            # they already have a device set
            view = Confirm(ctx, true_response="Alright, we'll swap your device!",
                            false_response="Cancelled adding device to your name.")
            change_name_prompt = await ctx.send('You already have a device in your nickname. Would you like to replace it?', view=view)
            # Wait for the View to stop listening for input...
            await view.wait()
            await change_name_prompt.delete()
            change_name = view.value
            
            if not change_name:
                await ctx.message.delete(delay=5)
                return
            else:
                # user wants to remove existing device, let's do that
                new_nick = re.sub(self.devices_remove_re, "", ctx.author.display_name).strip()
                if len(new_nick) > 32:
                    raise commands.BadArgument("Nickname too long")

        if not device.split(" ")[0].lower() in self.possible_devices:
            raise commands.BadArgument(
                "Unsupported device. Please see `!listdevices` for possible devices.")

        the_device = await self.find_device_from_ipsw_me(device)

        # did we find a device with given name?
        if the_device is None:
            raise commands.BadArgument("Device doesn't exist!")

        # prompt user for which firmware they want in their name
        firmware = await self.prompt_for_firmware(ctx, the_device)
        
        # change the user's nickname!
        if firmware is not None:
            name = the_device["name"]
            name = name.replace(' Plus', '+')
            name = name.replace('Pro Max', 'PM')
            new_nick = f"{new_nick} [{name}, {firmware}]"

            if len(new_nick) > 32:
                raise commands.BadArgument("Nickname too long! Aborting.")

            await ctx.author.edit(nick=new_nick)
            await ctx.send_success("Changed your nickname!", delete_after=5)
            await ctx.message.delete(delay=5)

    async def find_device_from_ipsw_me(self, device):
        """Get device metadata for a given device from IPSW.me API

        Parameters
        ----------
        device : str
            "Name of the device we want metadata for (i.e iPhone 12)"

        Returns
        -------
        dict
            "Dictionary with the relavent metadata
        """
        
        device = device.lower()
        async with aiohttp.ClientSession() as session:
            async with session.get(self.devices_url) as resp:
                if resp.status == 200:
                    data = await resp.text()
                    devices = json.loads(data)
                    devices.append(
                        {'name': 'iPhone SE 2', 'identifier': 'iPhone12,8'})

                    # try to find a device with the name given in command
                    for d in devices:
                        # remove regional version info of device i.e iPhone SE (CDMA) -> iPhone SE
                        name = re.sub(r'\((.*?)\)', "", d["name"])
                        # get rid of '[ and ']'
                        name = name.replace('[', '')
                        name = name.replace(']', '')
                        name = name.strip()

                        # are the names equal?
                        if name.lower() == device:
                            d["name"] = name
                            return d

    async def prompt_for_firmware(self, ctx, the_device):
        """Prompt user for the firmware they want to use in their name

        Parameters
        ----------
        the_device : dict
           "Metadata of the device we want firmware for. Must ensure this is a valid firmware for this device."

        Returns
        -------
        str
            "firmware version we want to use, or None if we want to cancel"
        """
        
        # retrieve list of available firmwares for the given device
        firmwares = await self.find_firmwares_from_ipsw_me(the_device)
        
        # prompt user to input an iOS version they want to put in their nickname
        prompt = context.PromptData(
            value_name="firmware",
            title="Please enter a version number.",
            description="Here are the 5 most recent...\n" + '\n'.join(firmware['version'] for firmware in firmwares[0:5]),
            convertor=str
        )

        firmware = await ctx.prompt(prompt)   
        found = False     
        
        # loop until we find a valid firmware or user cancels.
        while True:
            if firmware is None:
                await ctx.message.delete(delay=5)
                await ctx.send_warning("Cancelled.", delete_after=5)
                return
            
            # is this a valid version for this device?
            for f in firmwares:
                if f["version"] == firmware:
                    firmware = f["version"]
                    found = True
                    break

            if found:
                break
            else:
                prompt.reprompt = True
                firmware = await ctx.prompt(prompt)

        return firmware

    async def find_firmwares_from_ipsw_me(self, the_device):
        """Get list of all valid firmwares for a given device from IPSW.me

        Parameters
        ----------
        the_device : dict
            "Metadata of the device we want firmwares for"

        Returns
        -------
        list[dict]
            "list of all the firmwares"
        """
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.firmwares_url}/{the_device['identifier']}") as resp:
                if resp.status == 200:
                    firmwares = json.loads(await resp.text())["firmwares"]

        if len(firmwares) == 0:
            raise commands.BadArgument("Unforunately I don't have version history for this device.")

        return firmwares

    @commands.guild_only()
    @commands.bot_has_guild_permissions(change_nickname=True)
    @permissions.bot_channel_only_unless_mod()
    @permissions.ensure_invokee_role_lower_than_bot()
    @commands.command(name="removedevice")
    async def removedevice(self, ctx: context.Context) -> None:
        """Removes device from your nickname

        Example usage
        -------------
        !removedevice

        """

        if not re.match(self.devices_test, ctx.author.display_name):
            raise commands.BadArgument("You don't have a device nickname set!")

        new_nick = re.sub(self.devices_remove_re, "", ctx.author.display_name).strip()
        if len(new_nick) > 32:
            raise commands.BadArgument("Nickname too long")

        await ctx.author.edit(nick=new_nick)
        await ctx.message.delete(delay=5)
        await ctx.send_success("Removed device from your nickname!", delete_after=5)

    @commands.guild_only()
    @commands.bot_has_guild_permissions(change_nickname=True)
    @permissions.bot_channel_only_unless_mod()
    @commands.command(name="listdevices")
    async def listdevices(self, ctx: context.Context) -> None:
        """List all possible devices you can set your nickname to.

        Example usage
        -------------
        !listdevices
        """

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

        # stupid ipsw.me api doesn't have these devices
        devices_dict["iPhone"].add("iPhone SE 2")

        embed = discord.Embed(title="Devices list")
        embed.color = discord.Color.blurple()
        for key in devices_dict.keys():
            temp = list(devices_dict[key])
            temp.sort()
            embed.add_field(name=key, value=', '.join(
                map(str, temp)), inline=False)

        embed.set_footer(text=f"Requested by {ctx.author}")

        await ctx.message.reply(embed=embed)

    @removedevice.error
    @adddevice.error
    @listdevices.error
    async def info_error(self,  ctx: context.Context, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, permissions.PermissionsFailure)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await ctx.send_error(error)
        else:
            await ctx.send_error("A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Devices(bot))
