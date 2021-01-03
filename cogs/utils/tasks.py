import logging
from datetime import datetime

import discord
import random
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

        self.tasks = AsyncIOScheduler(
            jobstores=jobstores, executors=executors, job_defaults=job_defaults, event_loop=bot.loop)
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

        self.tasks.add_job(unmute_callback, 'date', id=str(
            id), next_run_time=date, args=[id], misfire_grace_time=3600)

    def schedule_remove_bday(self, id: int, date: datetime) -> None:
        """Create a task to remove birthday role from user given by ID `id`, at time `date`

        Parameters
        ----------
        id : int
            User to remove role
        date : datetime.datetime
            When to remove role
        """

        self.tasks.add_job(remove_bday_callback, 'date', id=str(
            id+1), next_run_time=date, args=[id], misfire_grace_time=3600)

    def cancel_unmute(self, id: int) -> None:
        """When we manually unmute a user given by ID `id`, stop the task to unmute them.

        Parameters
        ----------
        id : int
            User whose unmute task we want to cancel
        """

        self.tasks.remove_job(str(id), 'default')

    def cancel_unbirthday(self, id: int) -> None:
        """When we manually unset the birthday of a user given by ID `id`, stop the task to remove the role.
         Parameters
        ----------
        id : int
            User whose task we want to cancel
        """
        self.tasks.remove_job(str(id+1), 'default')
        
    def schedule_end_giveaway(self, channel_id: int, message_id: int, date: datetime, winners: int) -> None:
        """
        Create a task to end a giveaway with message ID `id`, at date `date`

        Parameters
        ----------
        channel_id : int
            ID of the channel that the giveaway is in
        message_id : int
            Giveaway message ID
        date : datetime.datetime
            When to end the giveaway
        """

        self.tasks.add_job(end_giveaway_callback, 'date', id=str(message_id+2), next_run_time=date, args=[channel_id, message_id, winners], misfire_grace_time=3600)

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
                    _id=bot_global.settings.guild().case_id,
                    _type="UNMUTE",
                    mod_id=bot_global.user.id,
                    mod_tag=str(bot_global.user),
                    reason="Temporary mute expired.",
                )
                await bot_global.settings.inc_caseid()
                await bot_global.settings.add_case(user.id, case)

                u = await bot_global.settings.user(id=user.id)
                u.is_muted = False
                u.save()

                log = await prepare_unmute_log(bot_global.user, user, case)

                log.remove_author()
                log.set_thumbnail(url=user.avatar_url)

                public_chan = guild.get_channel(
                    bot_global.settings.guild().channel_public)
                try:
                    await public_chan.send(embed=log)
                    await user.send(embed=log)
                except Exception:
                    pass
            else:
                case = Case(
                    _id=bot_global.settings.guild().case_id,
                    _type="UNMUTE",
                    mod_id=bot_global.user.id,
                    mod_tag=str(bot_global.user),
                    reason="Temporary mute expired.",
                )
                await bot_global.settings.inc_caseid()
                await bot_global.settings.add_case(id, case)

                u = await bot_global.settings.user(id=id)
                u.is_muted = False
                u.save()


def remove_bday_callback(id: int) -> None:
    """Callback function for actually unmuting. Creates asyncio task
    to do the actual unmute.

    Parameters
    ----------
    id : int
        User who we want to unmute
    """

    bot_global.loop.create_task(remove_bday(id))


async def remove_bday(id: int) -> None:
    """Remove the bday role of the user given by ID `id`

    Parameters
    ----------
    id : int
        User to remove role of
    """

    guild = bot_global.get_guild(bot_global.settings.guild_id)
    if guild is None:
        return

    bday_role = bot_global.settings.guild().role_birthday
    bday_role = guild.get_role(bday_role)
    if bday_role is None:
        return

    user = guild.get_member(id)
    await user.remove_roles(bday_role)

def end_giveaway_callback(channel_id: int, message_id: int, winners: int) -> None:
    """
    Callback function for ending a giveaway

    Parameters
    ----------
    channel_id : int
        ID of the channel that the giveaway is in
    message_id : int
        Message ID of the giveaway
    """

    bot_global.loop.create_task(end_giveaway(channel_id, message_id, winners))

async def end_giveaway(channel_id: int, message_id: int, winners: int) -> None:
    """
    End a giveaway.

    Parameters
    ----------
    channel_id : int
        ID of the channel that the giveaway is in
    message_id : int
        Message ID of the giveaway
    """

    guild = bot_global.get_guild(bot_global.settings.guild_id)
    channel = guild.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    embed = message.embeds[0]
    embed.set_footer(text="Ended")
    embed.timestamp = datetime.now()

    reaction = message.reactions[0]
    reacted_users = await reaction.users().flatten()
    reacted_ids = [user.id for user in reacted_users]
    reacted_ids.remove(bot_global.user.id)

    if len(reacted_ids) < winners:
        winners = len(reacted_ids)
    await bot_global.settings.add_giveaway(id=message.id, channel=channel_id, name=embed.title, entries=reacted_ids, winners=winners)
    
    rand_ids = random.sample(reacted_ids, winners)
    mentions = []
    for user_id in rand_ids:
        member = guild.get_member(user_id)
        while member is None or member.mention in mentions: # ensure that member hasn't left the server while simultaneously ensuring that we don't add duplicate members if we select a new random one
            member = guild.get_member(random.choice(g.entries))
        mentions.append(member.mention)

    await message.edit(embed=embed)
    await message.clear_reactions()

    if not mentions:
        await channel.send(f"No winner was selected for the giveaway of **{embed.title}** because nobody entered.")
        return

    if winners == 1:
        await channel.send(f"Congratulations {mentions[0]}! You won the giveaway of **{embed.title}**!")
    else:
        await channel.send(f"Congratulations {', '.join(mentions)}! You won the giveaway of **{embed.title}**!")
