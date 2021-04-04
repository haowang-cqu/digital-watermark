from flask import Flask, request
from PIL import Image
from wm.text2img import text2img
import base64
from io import BytesIO

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/getmark')
def getmark():
    fontname =  request.args.get('fontname', 'Microsoft YaHei')
    fontsize = int(request.args.get('fontsize', 15))
    text = request.args.get('text', 'Nothing')
    size = int(request.args.get('size', 100))
    img = text2img(text, size, 'RGB', fontname=fontname, fontsize=fontsize)
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    b64_img = base64.b64encode(buffered.getvalue()).decode()
    return 'data:image/jpeg;base64,' + b64_img


@app.route('/embed', methods=["POST"])
def embed():
    return ''


@app.route('/extract', methods=["POST"])
def extract():
    return ''