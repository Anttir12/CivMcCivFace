import logging

from sanic import Sanic, response

from civ_mc_civ_face.mc_civ_bot import CivMcCivFace

logger = logging.getLogger("server")

app = Sanic("CivBot")

bot: CivMcCivFace = None


@app.route("/")
async def index(request):
    return response.html('<p>Hello world!</p>')


@app.route("/test")
async def index(request):
    """ Simply to test if the container can connect to outside world"""
    import urllib.request
    page = urllib.request.urlopen("https://www.w3.org/Style/CSS/Test/CSS3/Selectors/current/html/static/index.html")
    content = page.read()
    logger.info(content)
    return response.html(content)


@app.route("/play-civ/webhook", methods=["POST"])
def play_civ_webhook(request):
    data = request.json
    logger.info("Received webhook! data:\n {}".format(data))
    bot.handle_webhook_message(data)
    return response.json({"status": "ok"})
