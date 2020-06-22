import os
import threading
import logging

from dotenv import load_dotenv
from flask import Flask, request

from app.civ_mc_civ_face.mc_civ_bot import CivMcCivFace

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = CivMcCivFace(command_prefix="!")


class App(Flask):

    def __init__(self, import_name):
        super().__init__(import_name)
        discord_bot = threading.Thread(target=self.run_bot, args=(bot,))
        discord_bot.start()

    def run_bot(self, bot):
        logger.info("Run bot called... TOKEN: {}".format(TOKEN))
        bot.run(TOKEN)


app = App("CivBot")


@app.route("/")
def index():
    logger.info("Frontpage called!")
    return "Hello"


@app.route("/play-civ/webhook", methods=["POST"])
def play_civ_webhook():
    logger.info("webhook call received")
    data = request.json
    bot.handle_webhook_message(data)
    return "OK"


if __name__ == "__main__":
    app.run()
