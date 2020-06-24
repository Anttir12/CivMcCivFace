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
bot = CivMcCivFace(command_prefix="!")


async def start_bot():
    logger.info("Staring bot with token: {}".format(TOKEN))
    await bot.start(TOKEN)


def main():
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    try:
        bot_thread = threading.Thread(target=loop.run_forever)
        bot_thread.start()
        # This is a blocking call. Exiting this should continue to stop the bot (loop)
        http_server.app.run(host='0.0.0.0', port=8888)
    finally:
        loop.stop()


if __name__ == "__main__":
    logger.info("Starting up...")
    main()
