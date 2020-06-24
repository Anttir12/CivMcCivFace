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


def main():
    discord_bot = threading.Thread(target=bot.run, args=(TOKEN,))
    logger.info("Staring bot with token: {}".format(TOKEN))
    discord_bot.start()
    http_server.app.run(port=8888)


if __name__ == "__main__":
    logger.info("Starting up...")
    main()
