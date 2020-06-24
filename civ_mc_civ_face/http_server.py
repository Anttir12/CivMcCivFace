from sanic import Sanic
from main import bot

app = Sanic("CivBot")

@app.route("/")
async def index(request):
    return "Hello"


@app.route("/play-civ/webhook", methods=["POST"])
def play_civ_webhook(request):
    data = request.json
    bot.handle_webhook_message(data)
    return "OK"
