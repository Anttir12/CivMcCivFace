import logging

from sanic import Sanic, response
from main import bot

logger = logging.getLogger("server")

app = Sanic("CivBot")


@app.route("/")
async def index(request):
    return response.html('<p>Hello world!</p>')


@app.route("/play-civ/webhook", methods=["POST"])
def play_civ_webhook(request):
    data = request.json
    bot.handle_webhook_message(data)
    return response.json({"status": "ok"})
