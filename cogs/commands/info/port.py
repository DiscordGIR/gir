import discord
from discord.ext import commands
from datetime import datetime
from data.case import Case
from data.cases import Cases
from data.guild import Guild
from data.user import User
from data.filterword import FilterWord
import dateutil.parser
import traceback
import asyncpg
import json
import pytz

class Port(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command(name="portfilter")
    async def printfilter(self, ctx):
        word_list = []
        filter_excluded_channel_list = []
        logging_excluded_channel_list = []
        conn = await asyncpg.connect('postgresql://emy@localhost/janet')
        async with conn.transaction():
            async for record in conn.cursor('SELECT * from guilds'):
                if record["id"] == "349243932447604736":
                    for word in record["filter.words"]:
                        word = json.loads(word)
                        new_word = FilterWord()
                        new_word.bypass = word["bypass"]
                        new_word.notify = word["notify"]
                        new_word.word = word["word"]

                        word_list.append(new_word)

                    for channel in record["filter.excludedChannels"]:
                        filter_excluded_channel_list.append(int(channel))
                    for channel in record["logging.excludedChannels"]:
                        logging_excluded_channel_list.append(int(channel))
        
        g = Guild.objects(_id=self.bot.settings.guild_id).first()
        g.filter_words = word_list
        g.save()

        g = Guild.objects(_id=349243932447604736).first()
        g.filter_words = word_list
        g.logging_excluded_channels = logging_excluded_channel_list
        g.filter_excluded_channels = filter_excluded_channel_list
        g.save()

        await ctx.send(f"Ported {len(word_list)} filtered words, {len(logging_excluded_channel_list)} logging excluded channels, {len(filter_excluded_channel_list)} filter excluded channels")


    @commands.guild_only()
    @commands.command(name="firsttime")
    async def firsttime(self, ctx):
        guild = Guild()
        guild._id = 777155838849843200

        guild.case_id = 1
        
        guild.role_mute = 777270186604101652
        guild.role_genius = 777270163589693482
        guild.role_moderator = 777270257772789770
        guild.role_memberplus = 777270242874359828
        guild.role_memberpro = 777270222868185158
        guild.role_memberedition = 777270206841880586
        guild.role_member = 777270914365784075
        
        guild.channel_public = 777270542033092638
        guild.channel_private = 777270554800422943
        guild.channel_reports = 777270579719569410
        guild.channel_botspam = 778233669881561088
        
        guild.logging_excluded_channels = [782765012510965781, 782765029735923722]
        guild.filter_excluded_channels = [782765012510965781, 782765029735923722]
        guild.save()

    @commands.guild_only()
    @commands.command(name="port")
    async def port(self, ctx):
        conn = await asyncpg.connect('postgresql://emy@localhost/janet')
        # Execute a statement to create a new table.
        user_count = 0
        case_count = 0
        async with conn.transaction():
            async for record in conn.cursor('SELECT * from users'):
                user = User()
                user._id = int(record["id"])
                user.is_clem = record["clem"]
                user.is_xp_frozen = record["xpFrozen"]
                user.warn_points = record["warnPoints"]
                user.was_warn_kicked = record["warnKicked"]
                user.xp = record["xp"]
                user.level = record["level"]
                user.offline_report_ping = record["offlineReportPing"]
                user.save()
                
                user_count += 1

                users_cases = record["cases"]
                cases = Cases()
                cases._id = record["id"]
                case_array = []
                if len(users_cases) > 0:
                    for case in users_cases:
                        case = json.loads(case)

                        if "id" in case:
                            case_count += 1
                            if case["id"] is None:
                                print("NOOOO")
                                print(case)
                            
                            new_case = Case()
                            new_case._id = case["id"]
                            new_case._type = case["type"]
                            new_case.date = datetime.utcfromtimestamp(case["date"]/1000)
                            if "until" in case:
                                new_case.until = pytz.utc.localize(datetime.utcfromtimestamp(case["date"]/1000))
                            if case["modID"] == "nooka#8966" or case["modID"] == "spooka#8966" or case["modID"] == "nooka#9999" or case["modID"] == "nooka#7474" or case["modID"] == "nooka#9999" or case["modID"] == "nooka#6969" or "nooka" in case["modID"]:
                                new_case.mod_id = 99656214966706176
                            elif case["modID"] == "Lepidus#0540":
                                new_case.mod_id = 342905593423462400
                            elif case["modID"] == "TheMrSkellytone#3411" or case["modID"] == "TheMrSkellytone#2000":
                                new_case.mod_id = 272756876972654592                        
                            elif case["modID"] == "Shady#0001" or case["modID"] == "TheMrSkellytone#2000":
                                new_case.mod_id = 351529578465984513                        
                            elif not case["modID"].isdigit():
                                new_case.mod_id = 12345
                                print("broken case", case)
                            else:
                                new_case.mod_id = case["modID"]
                            new_case.mod_tag = case["modTag"]
                            if "reason" in case:
                                new_case.reason = case["reason"]
                            else:
                                new_case.reason = "No reason."
                            if "punishment" in case:
                                new_case.punishment = str(case["punishment"])
                            new_case.lifted = False

                            case_array.append(new_case)
                cases.cases = case_array
                cases.save()
            print("DONE")
            async for record in conn.cursor('SELECT * from guilds'):
                if int(record["id"]) == 349243932447604736:
                    guild = Guild()
                    
                    guild.case_id = (await conn.fetchrow('SELECT "caseID" FROM "clientStorage" WHERE id = $1;', "688726074820919326"))["caseID"]
                    guild._id = record["id"]
                    guild.role_mute = record["roles.muted"]
                    guild.role_genius = record["roles.genius"]
                    guild.role_moderator = record["roles.moderator"]
                    guild.role_memberplus = record["roles.memberplus"]
                    guild.role_memberpro = record["roles.memberpro"]
                    guild.role_memberedition = record["roles.memberedition"]
                    guild.role_member = record["roles.member"]

                    guild.channel_public = record["channels.public"]
                    guild.channel_private = record["channels.private"]
                    guild.channel_reports = record["channels.reports"]
                    guild.channel_botspam = record["channels.botspam"]
                    
                    guild.nsa_guild_id = 687950909191618563

                    guild.save()


        await ctx.send(f"Migrated {user_count} users and {case_count} cases from Postgres db")

    @port.error
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
    bot.add_cog(Port(bot))
