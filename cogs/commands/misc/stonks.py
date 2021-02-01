import datetime as dt
import logging
import os
import traceback
import pytz
from io import BytesIO

import discord
import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import robin_stocks as r
from discord.ext import commands


class Stonks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        username = os.environ.get("RH_USER")
        password = os.environ.get("RH_PASS")
        mpl_logger = logging.getLogger('matplotlib')
        mpl_logger.setLevel(logging.WARNING)
        r.login(username,password)

    @commands.command(name="stonks")
    @commands.cooldown(2, 10, commands.BucketType.member)
    @commands.guild_only()
    async def stonks(self, ctx, symbol:str):
        async with ctx.typing():
            symbol_name = r.get_name_by_symbol(symbol)
            if symbol_name is None or symbol_name == "":
                raise commands.BadArgument("Invalid ticker symbol provided.")
            
            historical_data = r.stocks.get_stock_historicals(symbol, interval='5minute', span='day', bounds='extended', info=None)
            if historical_data is None or len(historical_data)  == 0:
                raise commands.BadArgument("An error occured fetching historical data for this symbol.")

            font = {'size'   : 20}
                    
            matplotlib.rc('font', **font)
            plt.style.use("seaborn-dark")
            for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
                plt.rcParams[param] = '#212946'  # bluish dark grey

            for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
                plt.rcParams[param] = '0.9'  # very light grey
            
            plt.figure(figsize=(20, 10))
            y = [round(float(data_point['open_price']),2) for data_point in historical_data]
            x = []
            z = [data_point['session'] for data_point in historical_data]

            eastern = pytz.timezone('US/Eastern')

            for data_point in historical_data:
                d = dt.datetime.strptime(data_point['begins_at'],'%Y-%m-%dT%H:%M:%SZ').astimezone(eastern)
                d = "{:d}:{:02d}".format(d.hour, d.minute)
                x.append(d)
            for x1, x2, y1,y2, z1,_ in zip(x, x[1:], y, y[1:], z, z[1:]):
                if z1 == 'reg':
                    plt.plot([x1, x2], [y1,y2] , 'g', linewidth=4)
                else:
                    plt.plot([x1, x2], [y1,y2] , color='gray', linewidth=4)

            x = np.array(x)
            frequency = 15
            # plot the data.
            plt.title("Stock price for {} over time".format(symbol_name))
            plt.xlabel("Time (EST)")
            plt.ylabel("Price")
            plt.xticks(x[::frequency], x[::frequency])

            plt.grid(color='#2A3459')  # bluish dark grey, but slightly lighter than background
            mp = mpatches.Patch(color='green', label='Market open')
            pmp = mpatches.Patch(color='gray', label='After hours')
            plt.legend(handles=[mp, pmp])
            
            
            b = BytesIO()
            plt.savefig(b, format='png')
            plt.close()
            b.seek(0)
            
            _file = discord.File(b, filename="image.png")
            await ctx.message.reply(file=_file, mention_author=False)

    @stonks.error
    async def info_error(self, ctx, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            await self.bot.send_error(ctx, "A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Stonks(bot))
