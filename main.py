import os
import threading

from dotenv import load_dotenv

from civ_mc_civ_face import http_server
from civ_mc_civ_face.mc_civ_bot import CivMcCivFace

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = CivMcCivFace(command_prefix="!")


def main():
    discord_bot = threading.Thread(target=bot.run, args=(TOKEN,))
    discord_bot.start()
    http_server.app.run(port=8888)


if __name__ == "__main__":
    main()
