import datetime as dt
import logging
import os
import traceback
import pytz
import seaborn as sns
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

            sns.set(font="Franklin Gothic Book",
                    rc={
            "axes.axisbelow": False,
            "axes.edgecolor": "#7289da",
            "axes.facecolor": "None",
            "axes.grid": False,
            "axes.labelcolor": "#7289da",
            "axes.spines.right": False,
            "axes.spines.top": False,
            "figure.facecolor": "#23272a",
            "lines.solid_capstyle": "round",
            "patch.edgecolor": "w",
            "patch.force_edgecolor": True,
            "text.color": "#fff",
            "xtick.bottom": False,
            "xtick.color": "#fff",
            "xtick.direction": "out",
            "xtick.top": False,
            "ytick.color": "#fff",
            "ytick.direction": "out",
            "ytick.left": False,
            "ytick.right": False})
            sns.set_context("notebook", rc={"font.size":20,
                                            "axes.titlesize":24,
                                            "axes.labelsize":18})
            # plt.figure(figsize=(20, 10))
            y = [round(float(data_point['open_price']),2) for data_point in historical_data]
            x = []
            z = [data_point['session'] for data_point in historical_data]
            fig, ax = plt.subplots()
            fig.set_figheight(10)
            fig.set_figwidth(20)            
            eastern = pytz.timezone('US/Eastern')

            for data_point in historical_data:
                d = dt.datetime.strptime(data_point['begins_at'],'%Y-%m-%dT%H:%M:%SZ').astimezone(eastern)
                d = "{:d}:{:02d}".format(d.hour, d.minute)
                x.append(d)
            for x1, x2, y1,y2, z1,_ in zip(x, x[1:], y, y[1:], z, z[1:]):
                if z1 == 'reg':
                    ax.plot([x1, x2], [y1,y2] , 'g', linewidth=4)
                else:
                    ax.plot([x1, x2], [y1,y2] , color='gray', linewidth=4)

            x = np.array(x)
            frequency = int(len(x)/6)
            # plot the data.
            fig.suptitle("Stock price for {} over time".format(symbol_name))
            ax.set_xlabel("Time (EST)", labelpad=20)
            ax.set_ylabel("Price", labelpad=20)
            plt.xticks(x[::frequency], x[::frequency])

            # plt.grid()  # bluish dark grey, but slightly lighter than background
            mp = mpatches.Patch(color='green', label='Market open')
            pmp = mpatches.Patch(color='gray', label='After hours')
            fig.legend(handles=[mp, pmp])
            
            ax.fill_between(x=x, y1=y, color="#7289da", alpha=0.3)
            
            ax.set_xlim(min(x), max(x))
            ax.set_ylim(min(y) - (0.1 * min(y)))
            
            b = BytesIO()
            fig.savefig(b, format='png')
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
