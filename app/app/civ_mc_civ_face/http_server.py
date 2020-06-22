import os

from flask import Flask, request

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

app = Flask("CivBot")
bot = None

@app.route("/")
def index():
    return "Hello"


@app.route("/play-civ/webhook", methods=["POST"])
def play_civ_webhook():
    data = request.json
    bot.handle_webhook_message(data)
    return "OK"