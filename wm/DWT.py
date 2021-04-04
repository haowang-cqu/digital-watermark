import pywt
import math
from PIL import Image, ImageDraw, ImageFont
from text2img import text2img
import numpy as np
import random
import cv2
np.set_printoptions(threshold=np.inf)
# def pre_process(pic_path,mark_text):
#     pic=Image.open(pic_path)
#     pic=pic.convert('L')#转换成灰度图
#     pic_array=np.array(pic).astype(np.float32)#转换成float32的numpy array
#     mark=text2img(mark_text,100,mode='1', fontsize=60)
#     mark_array=np.array(mark).astype(np.bool)
#     mark.save('mark.png')
#     return pic_array,mark_array

def embed_mark(pic_path,mark_path):
    '''
    输入要加入水印的图片路径，以及水印路径
    '''
    pic=Image.open(pic_path)
    pic=pic.convert('L')
    pic_array=np.array(pic).astype(np.float32)
    
    mark=Image.open(mark_path)
    mark_array=np.array(mark).astype(np.bool)

    pic_h,pic_w=pic_array.shape[:2]
    mark_h,mark_w=mark_array.shape[:2]
    mark_array_copy=mark_array.copy()
    #两次小波变化
    ca1,(ch1,cv1,cd1)=pywt.dwt2(pic_array,'haar')
    ca2,(ch2,cv2,cd2)=pywt.dwt2(ca1,'haar')
    ca2w=ca2.copy()#初始化嵌入水印的ca2系数
    random.seed(59433)
    ca2_size=ca2.shape[0]*ca2.shape[1]
    mark_array_copy_size=mark_array_copy.shape[0]*mark_array_copy.shape[1]
    #print(ca2_size,mark_array_copy_size)
    idx=random.sample(range(ca2_size),mark_array_copy_size)#生成一个范围在ca2_size，且有mark_array_copy_size个的数组
    ca2_flatten=ca2.flatten()
    mark_array_copy_flatten=mark_array_copy.flatten()
    for i in range(mark_array_copy_size):
        c=ca2_flatten[idx[i]]
        z=c%mark_w
        if mark_array_copy_flatten[i]:#水印对应二进制为1
            if z<mark_w/4:
                f=c-mark_w/4-z
            else:
                f=c+mark_w*3/4-z
        else:#水印对应二进制为0
            if z<mark_w*3/4:
                f=c+mark_w/4-z
            else:
                f=c+mark_w*5/4-z
        ca2_flatten[idx[i]]=f
    ca2w=ca2_flatten.reshape(ca2.shape)
    ca1w=pywt.idwt2((ca2w,(ch2,cv2,cd2)),'haar')
    picw=pywt.idwt2((ca1w,(ch1,cv1,cd1)),'haar')
    res_pic=picw
    res_pic=res_pic.astype(np.int)
    img=Image.fromarray(res_pic)
    img=img.convert("RGB")
    img.save('marked.png')
    
def excet_mark(marked_pic_path,mark_path):
    """
    输入嵌入水印后的图片路径以及水印的路径
    """
    marked_pic=Image.open(marked_pic_path).convert('L')
    mark=Image.open(mark_path)
    mark_array=np.array(mark).astype(np.bool)
    marked_pic_array=np.array(marked_pic).astype(np.float32)
    mark_h,mark_w=mark_array.shape[:2]
    ca1w,(ch1w,cv1w,cd1w)=pywt.dwt2(marked_pic_array,'haar')
    ca2w,(ch2w,cv2w,cd2w)=pywt.dwt2(ca1w,'haar')
    #print(ca2w.shape)

    mark_array_copy=mark_array.copy()
    random.seed(59433)
    ca2w_size=ca2w.shape[0]*ca2w.shape[1]
    mark_array_copy_size=mark_array_copy.shape[0]*mark_array_copy.shape[1]
    idx=random.sample(range(ca2w_size),mark_array_copy_size)
    res_mark=mark_array_copy.flatten()#就算是从新建立一个zeros矩阵初始化效果也一样
    ca2w_flatten=ca2w.flatten()
    for i in range(mark_array_copy_size):
        c=ca2w_flatten[idx[i]]
        z=c%mark_w
        if z<mark_w/2:
            res_mark[i]=False
        else:
            res_mark[i]=True
    #print(res_mark)
    res_mark=res_mark.reshape(mark_array.shape)
    img=Image.fromarray(res_mark)
    #img.show()
    img.save('get_mark.png')

        
# if __name__=='__main__':
#     # pic_path='C:\\Users\\LHW\\Desktop\\Lenna.png'
#     # pic_array,mark_array=pre_process(pic_path,"test")
#     embed_mark(pic_array,mark_array)
#     excet_mark('marked.png','mark.png')