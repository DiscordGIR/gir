import asyncio
import asyncpg
import os
from dotenv import find_dotenv, load_dotenv
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
import mongoengine

load_dotenv(find_dotenv())

async def migrate():
    print("STARTING MIGRATION...")
    conn = await asyncpg.connect(
        host     = os.environ.get("BOTTY_DBHOST"),
        database = os.environ.get("BOTTY_DB"),
        user     = os.environ.get("BOTTY_DBUSER"),
        password = os.environ.get("BOTTY_DBPASSWORD"),
    )

    user_count = 0
    case_count = 0
    word_count = 0
    async with conn.transaction():
        async for record in conn.cursor('SELECT * from users'):
            user = User()
            user._id = int(record["id"])
            user.is_clem = record["clem"]
            user.is_xp_frozen = record["xpFrozen"]
            user.was_warn_kicked = record["warnKicked"]
            user.xp = record["xp"]
            user.level = record["level"]
            user.offline_report_ping = record["offlineReportPing"]
            user.warn_points = record["warnPoints"]
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
                        elif case["modID"] == "Shady#0001":
                            new_case.mod_id = 438101365416263681                        
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
        async for record in conn.cursor('SELECT * from guilds'):
            if int(record["id"]) == 349243932447604736:
                guild = Guild()
                
                guild.case_id = (await conn.fetchrow('SELECT "caseID" FROM "clientStorage" WHERE id = $1;', "688726074820919326"))["caseID"]
                guild._id = os.environ.get("BOTTY_MAINGUILD")
                
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
                
                guild.nsa_guild_id = os.environ.get("BOTTY_NSAGUILD")

                word_list = []
                
                for word in record["filter.words"]:
                    word = json.loads(word)
                    if word["word"] == "discord.gg/":
                        continue
                    new_word = FilterWord()
                    new_word.bypass = word["bypass"]
                    new_word.notify = word["notify"]
                    new_word.word = word["word"]

                    word_count += 1
                    word_list.append(new_word)

                guild.filter_words = word_list
                guild.logging_excluded_channels = [ int(channel) for channel in record["logging.excludedChannels"] ]
                guild.filter_excluded_channels = [ int(channel) for channel in record["filter.excludedChannels"] ]
                guild.save()

        if os.environ.get("BOTTY_ENV"):
            # for dev server testing purposes
            guild = Guild.objects(_id=777155838849843200).first()
            
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

        print("DONE")
        print(f"Migrated {user_count} users and {case_count} cases, {word_count} filtered words from Postgres db")

if __name__ == "__main__":
        mongoengine.register_connection(alias="core", name="botty")
        res = asyncio.get_event_loop().run_until_complete( migrate() )