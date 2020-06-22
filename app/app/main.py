import os
import threading

from dotenv import load_dotenv

from app.civ_mc_civ_face import http_server
from app.civ_mc_civ_face.mc_civ_bot import CivMcCivFace

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


class App:

    def run(self):
        bot = CivMcCivFace(command_prefix="!")
        http_server = threading.Thread(target=self.run_server, args=(bot,))
        discord_bot = threading.Thread(target=self.run_bot, args=(bot,))

        discord_bot.start()
        http_server.start()


    def run_server(self, bot):
        http_server.bot = bot
        http_server.app.run()


    def run_bot(self, bot):
        bot.run(TOKEN)


app = App()

if __name__ == "__main__":
    app.run()
