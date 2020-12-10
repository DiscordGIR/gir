import asyncio
import os
from dotenv import find_dotenv, load_dotenv
from data.guild import Guild
import traceback
import mongoengine

load_dotenv(find_dotenv())

async def setup():
    print("STARTING SETUP...")
    guild = Guild()
    
    # you should have this setup in the .env file beforehand
    guild._id          = int(os.environ.get("BOTTY_MAINGUILD")
    guild.nsa_guild_id = os.environ.get("BOTTY_NSAGUILD")
    guild.case_id      = 1

    guild.role_mute          = 123  # put in the role IDs for your server here
    guild.role_genius        = 123  # put in the role IDs for your server here
    guild.role_moderator     = 123  # put in the role IDs for your server here
    guild.role_memberplus    = 123  # put in the role IDs for your server here
    guild.role_memberpro     = 123  # put in the role IDs for your server here
    guild.role_memberedition = 123  # put in the role IDs for your server here
    guild.role_member        = 123  # put in the role IDs for your server here
    guild.role_dev           = 123  # put in the role IDs for your server here

    guild.channel_public    = 123  # put in the channel IDs for your server here
    guild.channel_private   = 123  # put in the channel IDs for your server here
    guild.channel_reports   = 123  # put in the channel IDs for your server here
    guild.channel_botspam   = 123  # put in the channel IDs for your server here
    guild.channel_emoji_log = 123  # put in the channel IDs for your server here
   
    guild.logging_excluded_channels = []  # put in a channel if you want (ignored in logging)
    guild.filter_excluded_channels  = []  # put in a channel if you want (ignored in filter)
    guild.filter_excluded_guilds    = []  # put guild ID to whitelist in invite filter if you want
    guild.save()

    print("DONE")

if __name__ == "__main__":
        mongoengine.register_connection(alias="core", name="botty")
        res = asyncio.get_event_loop().run_until_complete( setup() )