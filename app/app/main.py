import os
import threading

from dotenv import load_dotenv
from flask import Flask, request

from app.civ_mc_civ_face.mc_civ_bot import CivMcCivFace

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = CivMcCivFace(command_prefix="!")


class App(Flask):

    def run(self, **kwargs):
        discord_bot = threading.Thread(target=self.run_bot, args=(bot,))
        discord_bot.start()
        super().run(**kwargs)

    def run_bot(self, bot):
        bot.run(TOKEN)


app = App("CivBot")


@app.route("/")
def index():
    return "Hello"


@app.route("/play-civ/webhook", methods=["POST"])
def play_civ_webhook():
    data = request.json
    bot.handle_webhook_message(data)
    return "OK"


if __name__ == "__main__":
    app.run()
