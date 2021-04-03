import numpy as np
import math
from PIL import Image, ImageDraw, ImageFont
import scipy
from text2img import *


def insert_mark(pic_path,mark_path):
    mark=text2img(u"test", 100, 100, mode='1', fontsize=30)
    block_width = 8
    im=Image.open(pic_path)
    im_array = np.array(im)
    mark_array=np.array(mark)
    row=mark_array.shape[0]
    col=mark_array.shape[1]
    for i in range(row):
        for j in range(col):
            BLOCK=np.float32(im_array[i*block_width:i*block_width+block_width,j*block_width:j*block_width+block_width])
            BLOCK=scipy.fft.dct(BLOCK)
            if mark_array[i][j]==False:
                a=-1
            else:
                a=1
            BLOCK=BLOCK*(1+a*0.03)
            BLOCK=scipy.fft.idct(BLOCK).astype(np.uint8)
            im_array[i*block_width:i*block_width+block_width,j*block_width:j*block_width+block_width]=BLOCK
    img = Image.fromarray(im_array)
    img.save('DCT_RES.png')
    #img.show()
    

def dct_decode(pic_path,marked_path):
    block_width=8
    im=Image.open(pic_path)
    im_array=np.array(im)
    marked=Image.open(marked_path)
    marked_array=np.array(marked)
    row=im_array.shape[0]//block_width
    col=im_array.shape[1]//block_width
    decode_pic=np.zeros((row,col)).astype(np.bool)
    for i in range(row):
        for j in range(col):
            BLOCK_ORIGIN=np.float32(im_array[i*block_width:i*block_width+block_width,j*block_width:j*block_width+block_width])
            BLOCK_MARKED=np.float32(marked_array[i*block_width:i*block_width+block_width,j*block_width:j*block_width+block_width])
            BLOCK_ORIGIN=scipy.fft.idct(BLOCK_ORIGIN)
            BLOCK_MARKED=scipy.fft.idct(BLOCK_MARKED)
            
            bm=BLOCK_MARKED[1,1,2]
            bo=BLOCK_ORIGIN[1,1,2]
            a=bm/bo-1
            # print(a)
            if a<0:
                decode_pic[i,j]=False
            else:
                decode_pic[i,j]=True
    img=Image.fromarray(decode_pic)
    img.show()
    img.save('decode_dct.png')


# insert_mark("test1.png","test.png")
dct_decode("test1.png",'DCT_RES.png')
