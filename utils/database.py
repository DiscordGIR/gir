from model.guild import Guild
from utils.logger import logger
from utils.config import cfg
import mongoengine
import os


class Database:
    def __init__(self):
        logger.info("Starting database...")
        mongoengine.register_connection(
            host=os.environ.get("DB_HOST"), port=int(os.environ.get("DB_PORT")), alias="default", name="botty")
        logger.info("Database connected and loaded successfully!")
        
        if not Guild.objects(_id=cfg.guild_id):
            raise Exception(f"The database has not been set up for guild {cfg.guild_id}! Please refer to README.md.")
        
    def guild(self) -> Guild:
        """Returns the state of the main guild from the database.

        Returns
        -------
        Guild
            The Guild document object that holds information about the main guild.
        """

        return Guild.objects(_id=cfg.guild_id).first()


db = Database()