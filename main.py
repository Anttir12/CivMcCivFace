import os
import threading

from flask import Flask, request

from play_civ_bot import CivMcCivFace

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

app = Flask("CivBot")
civ_mc_civ_face = CivMcCivFace()


def run_server():
    app.run()


def run_bot():
    civ_mc_civ_face.run(TOKEN)


@app.route("/")
def index():
    return "Hello"


@app.route("/play-civ/webhook", methods=["POST"])
def play_civ_webhook():
    data = request.json
    civ_mc_civ_face.handle_webhook_message(data)
    return "OK"


http_server = threading.Thread(target=run_server)
discord_bot = threading.Thread(target=run_bot)
http_server.start()
discord_bot.start()

