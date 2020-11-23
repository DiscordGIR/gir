from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.job import Job
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.date import DateTrigger
import pytz
import logging
import datetime
import time
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

class Scheduler():
    def __init__(self, bot):
        global bot_global
        self.bot = bot
        bot_global = bot
        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)

        self.scheduler = AsyncIOScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, event_loop=self.bot.loop)
        self.scheduler.start()

    def add_mute(self, id, date):
        self.scheduler.add_job(mute_callback, 'date', id=str(id), next_run_time=date, args=[id])

    def manual_unmute(self, id):
        self.scheduler.remove_job(str(id), 'default')

def mute_callback(id):
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