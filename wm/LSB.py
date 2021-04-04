import numpy as np
from PIL import Image
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from wm.text2img import text2img
from wm.arnold import arnold_encode, arnold_decode


def embed_LSB(pic, mark, confuse=False):
    if confuse:
        mark = arnold_encode(mark)
    pic = np.array(pic)
    mark = np.array(mark)
    for i in range(mark.shape[0]):
        for j in range(mark.shape[1]):
            blue = pic[i, j, 2]
            pic[i, j, 2] = blue - blue % 2 + mark[i][j]
    return Image.fromarray(pic)


def extract_LSB(pic, confuse=False):
    pic = np.array(pic)
    mark = np.zeros((pic.shape[0], pic.shape[1])).astype(np.bool)
    for i in range(pic.shape[0]):
        for j in range(pic.shape[1]):
            mark[i, j] = pic[i, j, 2] % 2
    mark = Image.fromarray(mark)
    if confuse:
        mark = arnold_encode(mark)
    return mark


if __name__=='__main__':
    mark = text2img(u'测试水印', 300, mode='1', fontsize=50)
    pic = Image.open('temp/lena.png')
    confuse = False
    pic_marked = embed_LSB(pic, mark, confuse=confuse)
    pic_marked.save('temp/lsb_pic_marked.png')
    ext_mark = extract_LSB(pic_marked, confuse=confuse)
    ext_mark.save('temp/lsb_ext_mark.png')