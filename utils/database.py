import os

import mongoengine
from data.model.guild import Guild

from utils.config import cfg
from utils.logger import logger


class Database:
    def __init__(self):
        logger.info("Starting database...")
        mongoengine.register_connection(
            host=os.environ.get("DB_HOST"), port=int(os.environ.get("DB_PORT")), alias="default", name="botty")
        logger.info("Database connected and loaded successfully!")
        
        if not Guild.objects(_id=cfg.guild_id):
            raise Exception(f"The database has not been set up for guild {cfg.guild_id}! Please refer to README.md.")


db = Database()
