import asyncio
import logging
from datetime import datetime

import discord
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cogs.utils.logs import prepare_unmute_log
from data.case import Case

jobstores = {
    'default': MongoDBJobStore(database="botty", collection="jobs", host="127.0.0.1"),
}

executors = {
    'default': ThreadPoolExecutor(20)
}

job_defaults = {
    # 'coalesce': True
}

bot_global = None

class Tasks():
    """Job scheduler for unmute, using APScheduler
    """

    def __init__(self, bot: discord.Client):
        """Initialize scheduler

        Parameters
        ----------
        bot : discord.Client
            instance of Discord client
        """ 

        global bot_global
        bot_global = bot

        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)

        self.tasks = AsyncIOScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, event_loop=bot.loop)
        self.tasks.start()

    def schedule_unmute(self, id: int, date: datetime) -> None:
        """Create a task to unmute user given by ID `id`, at time `date`

        Parameters
        ----------
        id : int
            User to unmute
        date : datetime.datetime
            When to unmute
        """        

        self.tasks.add_job(unmute_callback, 'date', id=str(id), next_run_time=date, args=[id], misfire_grace_time=3600)

    def cancel_unmute(self, id: int) -> None:
        """When we manually unmute a user given by ID `id`, stop the task to unmute them.

        Parameters
        ----------
        id : int
            User whose unmute task we want to cancel
        """        

        self.tasks.remove_job(str(id), 'default')

def unmute_callback(id: int) -> None:
    """Callback function for actually unmuting. Creates asyncio task
    to do the actual unmute.

    Parameters
    ----------
    id : int
        User who we want to unmute
    """    

    bot_global.loop.create_task(remove_mute(id))

async def remove_mute(id: int) -> None:
    """Remove the mute role of the user given by ID `id`

    Parameters
    ----------
    id : int
        User to unmute
    """    

    guild = bot_global.get_guild(bot_global.settings.guild_id)
    if guild is not None:
        mute_role = bot_global.settings.guild().role_mute
        mute_role = guild.get_role(mute_role)
        if mute_role is not None:
            user = guild.get_member(id)
            if user is not None:
                await user.remove_roles(mute_role)
                case = Case(
                    _id = bot_global.settings.guild().case_id,
                    _type = "UNMUTE",
                    mod_id=bot_global.user.id,
                    mod_tag = str(bot_global.user),
                    reason="Temporary mute expired.",
                )
                await bot_global.settings.inc_caseid()
                await bot_global.settings.add_case(user.id, case)

                u = await bot_global.settings.user(id=user.id)
                u.muted = True
                u.save()

                log = await prepare_unmute_log(bot_global.user, user, case)
                
                log.remove_author()
                log.set_thumbnail(url=user.avatar_url)

                public_chan = guild.get_channel(bot_global.settings.guild().channel_public)
                try:
                    await public_chan.send(embed=log)
                    await user.send(embed=log)
                except:
                    pass
