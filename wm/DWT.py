import pywt
import math
from PIL import Image, ImageDraw, ImageFont
from wm.text2img import text2img
import numpy as np
import random
np.set_printoptions(threshold=np.inf)
# def pre_process(pic_path,mark_text):
#     pic=Image.open(pic_path)
#     pic=pic.convert('L')#转换成灰度图
#     pic_array=np.array(pic).astype(np.float32)#转换成float32的numpy array
#     mark=text2img(mark_text,100,mode='1', fontsize=60)
#     mark=np.array(mark).astype(np.bool)
#     mark.save('mark.png')
#     return pic_array,mark


def embed_DWT(pic, mark):
    pic = np.array(pic)
    blue = pic[:, :, 2].copy().astype(np.float32)
    mark = np.array(mark).astype(np.bool)

    pic_h, pic_w = blue.shape[:2]
    mark_h, mark_w = mark.shape[:2]
    mark_copy = mark.copy()
    # 两次小波变化
    ca1, (ch1, cv1, cd1) = pywt.dwt2(blue, 'haar')
    ca2, (ch2, cv2, cd2) = pywt.dwt2(ca1, 'haar')
    ca2w = ca2.copy()  # 初始化嵌入水印的ca2系数
    random.seed(59433)
    ca2_size = ca2.shape[0]*ca2.shape[1]
    mark_copy_size = mark_copy.shape[0]*mark_copy.shape[1]
    # print(ca2_size,mark_copy_size)
    # 生成一个范围在ca2_size，且有mark_copy_size个的数组
    idx = random.sample(range(ca2_size), mark_copy_size)
    ca2_flatten = ca2.flatten()
    mark_copy_flatten = mark_copy.flatten()
    for i in range(mark_copy_size):
        c = ca2_flatten[idx[i]]
        z = c % mark_w
        if mark_copy_flatten[i]:  # 水印对应二进制为1
            if z < mark_w/4:
                f = c-mark_w/4-z
            else:
                f = c+mark_w*3/4-z
        else:  # 水印对应二进制为0
            if z < mark_w*3/4:
                f = c+mark_w/4-z
            else:
                f = c+mark_w*5/4-z
        ca2_flatten[idx[i]] = f
    ca2w = ca2_flatten.reshape(ca2.shape)
    ca1w = pywt.idwt2((ca2w, (ch2, cv2, cd2)), 'haar')
    picw = pywt.idwt2((ca1w, (ch1, cv1, cd1)), 'haar')
    res_pic = picw
    res_pic = res_pic.astype(np.int)
    pic[:, :, 2] = res_pic
    return Image.fromarray(pic)


def extract_DWT(marked, mark):
    marked = np.array(marked)
    blue = marked[:, :, 2].copy().astype(np.float32)
    mark = np.array(mark).astype(np.bool)
    mark_h, mark_w = mark.shape[:2]
    ca1w, (ch1w, cv1w, cd1w) = pywt.dwt2(blue, 'haar')
    ca2w, (ch2w, cv2w, cd2w) = pywt.dwt2(ca1w, 'haar')
    mark_copy = mark.copy()
    random.seed(59433)
    ca2w_size = ca2w.shape[0]*ca2w.shape[1]
    mark_copy_size = mark_copy.shape[0]*mark_copy.shape[1]
    idx = random.sample(range(ca2w_size), mark_copy_size)
    res_mark = mark_copy.flatten()  # 就算是从新建立一个zeros矩阵初始化效果也一样
    ca2w_flatten = ca2w.flatten()
    for i in range(mark_copy_size):
        c = ca2w_flatten[idx[i]]
        z = c % mark_w
        if z < mark_w/2:
            res_mark[i] = False
        else:
            res_mark[i] = True
    res_mark = res_mark.reshape(mark.shape)
    img = Image.fromarray(res_mark)
    return img


if __name__=='__main__':
    mark = text2img(u'测试水印', 50, mode='1', fontsize=20)
    mark.save('temp/DWT_mark.png')
    pic = Image.open('temp/lena.png')
    pic_marked = embed_DWT(pic, mark)
    pic_marked.save('temp/DWT_pic_marked.png')
    ext_mark = extract_DWT(pic_marked, Image.open('temp/DWT_mark.png'))
    ext_mark.save('temp/DWT_ext_mark.png')
    # extract_DWT(Image.open('temp/a-pic.png'), Image.open('temp/a-mark.png')).show()