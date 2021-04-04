from flask import Flask, request, make_response
from flask_cors import CORS
from PIL import Image
from wm.text2img import text2img
import base64
from io import BytesIO
import os
import uuid

from wm.LSB import embed_LSB, extract_LSB
from wm.DCT import embed_DCT, extract_DCT
from wm.DWT import embed_DWT, extract_DWT

app = Flask(__name__)
CORS(app)  # 跨域

# 设置图片缓存目录
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'temp')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER']) 

# 文件类型过滤
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


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
    b64_img = 'data:image/jpeg;base64,' + base64.b64encode(buffered.getvalue()).decode()
    return {'status': 'ok', 'image': b64_img}


def can_embed(algorithm, pic_size, mark_size):
    if algorithm == 'LSB':
        if mark_size > pic_size:
            return False
    elif algorithm == 'DCT':
        if mark_size > pic_size // 8:
            return False
    else:
        if mark_size > pic_size // 4:
            return False
    return True


def do_embed(algorithm, pic, mark):
    if algorithm == 'LSB':
        marked = embed_LSB(pic, mark)
    elif algorithm == 'DCT':
        marked = embed_DCT(pic, mark)
    else:
        marked = embed_DCT(pic, mark)
    return marked


@app.route('/embed', methods=["POST"])
def embed():
    image = request.files.get('image')
    algorithm = request.form.get('algorithm')
    fontname = request.form.get('fontname')
    fontsize = request.form.get('fontsize')
    size = request.form.get('size')
    text = request.form.get('text')
    save_name = str(uuid.uuid4())+'.png'
    if not all([image, algorithm, fontname, fontsize, size, text]):
        return {'status': 'error', 'msg': '参数不能为空'}
    fontsize = int(fontsize)
    size = int(size)
    pic = Image.open(image)
    width = pic.width
    height = pic.height
    if not can_embed(algorithm, min(width, height), size):
        return {'status': 'error', 'msg': '嵌入失败，水印太大'}
    # 生成水印
    mark = text2img(text, size, fontname=fontname, fontsize=fontsize)
    mark.save(os.path.join(app.config['UPLOAD_FOLDER'], 'mark-'+save_name))
    # 嵌入水印
    marked_pic = do_embed(algorithm, pic, mark)
    marked_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], 'marked-pic-'+save_name))
    return {'status': 'ok', 'mark': 'mark-'+save_name, 'marked_pic': 'marked-pic-'+save_name}


@app.route('/extract', methods=["POST"])
def extract():
    algorithm = request.form.get('algorithm')
    marked_pic = request.files.get('marked_pic')
    pic = request.files.get('pic')
    mark = request.files.get('mark')
    if algorithm == 'LSB':
        ext_mark = extract_LSB(Image.open(marked_pic))
    elif algorithm == 'DCT':
        ext_mark = extract_DCT(Image.open(pic), Image.open(marked_pic))
    else:
        ext_mark = extract_DWT(Image.open(marked_pic), Image.open(mark))
    buffered = BytesIO()
    ext_mark.save(buffered, format="JPEG")
    b64_img = 'data:image/jpeg;base64,' + base64.b64encode(buffered.getvalue()).decode()
    return {'status': 'ok', 'mark': b64_img}


@app.route('/temp/<string:filename>', methods=['GET'])
def get_img(filename):
    if filename is None:
        pass
    else:
        image_data = open(os.path.join(app.config['UPLOAD_FOLDER'], '%s' % filename), "rb").read()
        response = make_response(image_data)
        response.headers['Content-Type'] = 'image/png'
        return response