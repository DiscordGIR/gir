from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import logging
import asyncio

import discord

jobstores = {
    'default': MongoDBJobStore(database="botty", collection="jobs", host="127.0.0.1"),
}

executors = {
    'default': ThreadPoolExecutor(20)
}

job_defaults = {
    'coalesce': True
}

bot_global = None

class Tasks():
    def __init__(self, bot):
        global bot_global
        self.bot = bot
        bot_global = bot

        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)

        self.tasks = AsyncIOScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, event_loop=self.bot.loop)
        self.tasks.start()

    def schedule_unmute(self, id, date):
        self.tasks.add_job(unmute_callback, 'date', id=str(id), next_run_time=date, args=[id])

    def cancel_unmute(self, id):
        self.tasks.remove_job(str(id), 'default')

def unmute_callback(id):
    bot_global.loop.create_task(remove_mute(id))

async def remove_mute(id):
    guild = bot_global.get_guild(bot_global.settings.guild_id)
    if guild is not None:
        mute_role = bot_global.settings.guild().role_mute
        mute_role = guild.get_role(mute_role)
        if mute_role is not None:
            user = guild.get_member(id)
            if user is not None:
                await user.remove_roles(mute_role)