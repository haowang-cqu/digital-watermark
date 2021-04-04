import numpy as np
import math
from PIL import Image, ImageDraw, ImageFont
import scipy
from text2img import *


def embed_DCT(pic, mark):
    block_width = 8
    im_array = np.array(pic)
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
            BLOCK[:,:,2]=BLOCK[:,:,2]*(1+a*0.03)
            BLOCK=scipy.fft.idct(BLOCK).astype(np.uint8)
            im_array[i*block_width:i*block_width+block_width,j*block_width:j*block_width+block_width]=BLOCK
    img = Image.fromarray(im_array)
    return img
    

def extract_DCT(pic,marked):
    block_width=8
    im_array=np.array(pic)
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
            if a<0:
                decode_pic[i,j]=False
            else:
                decode_pic[i,j]=True
    img=Image.fromarray(decode_pic)
    return img

if __name__=='__main__':
    from text2img import text2img
    mark = text2img(u'测试水印', 60, mode='1', fontsize=20)
    pic = Image.open('temp/lena.png')
    pic_marked=embed_DCT(pic,mark)
    pic_marked.save('temp/DCT_pic_marked.png')
    ext_mark=extract_DCT(pic,pic_marked)
    ext_mark.save('temp/DCT_ext_mark.png')