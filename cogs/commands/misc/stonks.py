import datetime as dt
import logging
import os
import traceback
import pytz
import seaborn as sns
import humanize
from io import BytesIO

import discord
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import robin_stocks as r
from coinmarketcapapi import CoinMarketCapAPI
from discord.ext import commands


class Stonks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        username = os.environ.get("RH_USER")
        password = os.environ.get("RH_PASS")
        mpl_logger = logging.getLogger('matplotlib')
        mpl_logger.setLevel(logging.WARNING)

        r.login(username,password)
        self.cmc = CoinMarketCapAPI(os.environ.get("CMC_KEY"))

        self.last_checked_cache = {}
        """ 
            {
                123456: {
                    "GME": {
                        "last_price": 213.12,
                        "last_checked": datetime
                    },
                    ...
                },
                ...
            }
        """
    @commands.command(name="sc")
    @commands.cooldown(2, 10, commands.BucketType.member)
    @commands.guild_only()
    async def stonks(self, ctx, ticker:str):
        """Graph price of a stock against time

        Example usage
        -------------
        !sc gme

        Parameters
        ----------
        ticker : str
            ticker of the stock, i.e btc
        """
        await self.do_graph(ctx, ticker)
    
    @commands.command(name="cc")
    @commands.cooldown(2, 10, commands.BucketType.member)
    @commands.guild_only()
    async def crypto(self, ctx, symbol:str):
        """Graph the price of a cryptocurrency against time

        Example usage
        -------------
        !cc btc

        Parameters
        ----------
        symbol : str
            Symbol of the coin, i.e btc
        """
        await self.do_graph(ctx, symbol, False)
    
    async def do_graph(self, ctx, symbol:str, stocks=True):
        stonks_chan = self.bot.settings.guild().channel_stonks
        if not self.bot.settings.permissions.hasAtLeast(ctx.guild, ctx.author, 5) and ctx.channel.id != stonks_chan:
            raise commands.BadArgument(f"Command only allowed in <#{stonks_chan}>")

        async with ctx.typing():
            if stocks:
                symbol_name = r.get_name_by_symbol(symbol)
                if symbol_name is None or symbol_name == "":
                    raise commands.BadArgument("Invalid ticker symbol provided.")
                historical_data = r.stocks.get_stock_historicals(symbol, interval='5minute', span='day', bounds='extended', info=None)
                if historical_data is None or len(historical_data)  == 0:
                    raise commands.BadArgument("An error occured fetching historical data for this symbol.")
                
            else:
                symbol_name = symbol.upper()
                try:
                    historical_data = r.crypto.get_crypto_historicals(symbol, interval='5minute', span='day', bounds='extended', info=None)
                except:
                    try:
                        data = self.cmc.cryptocurrency_quotes_latest(symbol=symbol).data[symbol_name]
                    except Exception:
                        raise commands.BadArgument("Invalid ticker symbol provided.")

                    embed = discord.Embed(title=f"{data['name']} ({data['symbol']})")
                    embed.description = "Sorry, we weren't able to generate a graph for this coin. Here's the current price."
                    embed.add_field(name="Price", value='$' + str(round(data['quote']['USD']['price'], 4)))
                    embed.color = discord.Color.blurple()
                    await ctx.message.reply(embed=embed)
                    return

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
            "ytick.right": False}, font_scale=1.75)
            
            
            y = [round(float(data_point['open_price']),2 if stocks else 4) for data_point in historical_data]
            x = []
            z = [data_point['session'] for data_point in historical_data]
            lower_limit =  min(y) - (0.05 * min(y))
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
                    ax.plot([x1, x2], [y1,y2] , color='#7289da', linewidth=2)
                else:
                    ax.plot([x1, x2], [y1,y2] , color='#99aab5', linewidth=2)
                if y1 < y2:
                    plt.bar(x2, lower_limit + (y2-y1), 1, color="#2ECC40")
                else:
                    plt.bar(x2, lower_limit + (y1-y2), 1, color="#FF4136")
            x = np.array(x)
            
            print("x",x)
            print("y",y)
            
            frequency = int(len(x)/6) if len(x) > 6 else 1
            # plot the data.
            if not stocks:
                data = self.cmc.cryptocurrency_quotes_latest(symbol=symbol).data[symbol_name]
                current_price = round(data['quote']['USD']['price'], 4)
                fig.suptitle(f"{data['name']} ({data['symbol']}) - ${current_price}")
            else:
                current_price = y[-1]
                fig.suptitle(f"{symbol_name} - ${current_price}")
            ax.set_xlabel("Time (EST)", labelpad=20)
            ax.set_ylabel("Price (USD)", labelpad=20)
            plt.xticks(x[::frequency], x[::frequency])

            mp = mpatches.Patch(color='#7289DA', label='Market open')
            pmp = mpatches.Patch(color='#99aab5', label='After hours')
            fig.legend(handles=[mp, pmp])
            
            ax.fill_between(x=x, y1=y, color="#7289da", alpha=0.3)
            
            ax.set_ylim(lower_limit)
            
            b = BytesIO()
            fig.savefig(b, format='png')
            plt.close()
            b.seek(0)
            
            _file = discord.File(b, filename="image.png")
            
            text = ""            
            if ctx.author.id in self.last_checked_cache:
                if symbol_name in self.last_checked_cache[ctx.author.id]:
                    obj = self.last_checked_cache[ctx.author.id][symbol_name]
                    time_delta = humanize.naturaltime(dt.datetime.now() - obj["last_checked"])
                    price_percentage = round(((obj["last_price"] / current_price) - 1) * 100, 3)
                    
                    if price_percentage >= 0:
                        price_percentage = "+" + str(price_percentage)
                        
                    text = f"You last checked this price {time_delta}\nPrice difference since then: {price_percentage}%"
                self.last_checked_cache[ctx.author.id][symbol_name] = { "last_price": current_price, "last_checked": dt.datetime.now()}

            else:
                self.last_checked_cache[ctx.author.id] = {symbol_name: { "last_price": current_price, "last_checked": dt.datetime.now()}}

            await ctx.message.reply(text, file=_file, mention_author=False)

    @crypto.error
    @stonks.error
    async def info_error(self, ctx, error):
        await ctx.message.delete(delay=5)
        if (isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
            or isinstance(error, commands.BadUnionArgument)
            or isinstance(error, commands.MissingPermissions)
            or isinstance(error, commands.BotMissingPermissions)
            or isinstance(error, commands.CommandOnCooldown)
            or isinstance(error, commands.MaxConcurrencyReached)
                or isinstance(error, commands.NoPrivateMessage)):
            await self.bot.send_error(ctx, error)
        else:
            await self.bot.send_error(ctx, "A fatal error occured. Tell <@109705860275539968> about this.")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Stonks(bot))
