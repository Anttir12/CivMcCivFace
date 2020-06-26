import asyncio
import os
import threading
import logging.config

from dotenv import load_dotenv

from civ_mc_civ_face import http_server
from civ_mc_civ_face.mc_civ_bot import CivMcCivFace

logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)

logger = logging.getLogger("mcciv")

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_NAME = os.getenv("DISCORD_GUILD_NAME")

GAME_FILE = os.getenv("GAME_FILE_PATH")
GLOBAL_SETTINGS = os.getenv("GLOBAL_SETTINGS")
bot_location = os.getcwd()
if not GAME_FILE:
    GAME_FILE = os.path.join(bot_location, ".bot_data", "game_file.json")
if os.path.exists(GAME_FILE):
    if not os.path.isfile(GAME_FILE):
        raise Exception("{} exists and is not a file!")
else:
    os.makedirs(os.path.dirname(GAME_FILE), exist_ok=True)
    with open(GAME_FILE, "w") as file:
        file.write("{}")
if not GLOBAL_SETTINGS:
    GLOBAL_SETTINGS = os.path.join(bot_location, ".bot_data", "global_settings.json")
if os.path.exists(GLOBAL_SETTINGS):
    if not os.path.isfile(GLOBAL_SETTINGS):
        raise Exception("{} exists and is not a file!")
else:
    os.makedirs(os.path.dirname(GLOBAL_SETTINGS), exist_ok=True)
    with open(GLOBAL_SETTINGS, "w") as file:
        file.write("{}")


async def start_bot(bot):
    logger.info("Staring bot")
    await bot.start(TOKEN)


def main():
    bot = CivMcCivFace(GAME_FILE, GUILD_NAME, GLOBAL_SETTINGS, command_prefix="!")
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot(bot))
    try:
        bot_thread = threading.Thread(target=loop.run_forever)
        bot_thread.start()
        # This is a blocking call. Exiting this should continue to stop the bot (loop)
        http_server.bot = bot
        http_server.app.run(host='0.0.0.0', port=8888)
    finally:
        loop.stop()


if __name__ == "__main__":
    logger.info("Starting up...")
    main()
