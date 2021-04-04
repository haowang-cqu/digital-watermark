import cv2 as cv
import numpy as np
import math

def insert_watermark(pic_path, mark_path, count=None):
    pic=cv.imread(pic_path)
    mark=cv.imread(mark_path)

    gray_mark=cv.cvtColor(mark,cv.COLOR_BGR2GRAY)
    ret,result_mark=cv.threshold(gray_mark,70,255,1)
    cv.imwrite("DCT_mark.jpg",result_mark,[int(cv.IMWRITE_JPEG_QUALITY),95])
    #处理原本图片
    #pic进行YUV格式化
    pic_YUV=cv.cvtColor(pic,cv.COLOR_RGB2YUV)
    #使用DCT必须转成float32
    pic_YUV_float32=pic_YUV.astype('float32')

    #开始嵌入
    water_mark=pic_YUV_float32
    #使用block矩阵，并使得它等于pic
    block_water_mark=np.zeros([pic_YUV_float32.shape[0],pic_YUV_float32.shape[1],3],np.float32)
    block_water_mark[:,:,:]=pic_YUV_float32[:,:,:]
    #以8*8block为单位进行运算
    #竖着看下来8*8block的个数
    block_8x8_row=int(pic_YUV_float32.shape[0]/8)
    #横着看下来8*8block的个数
    block_8x8_col=int(pic_YUV_float32.shape[1]/8)

    #每个8*8像素块所包含的水印像素
    r=math.ceil((result_mark.shape[0]*result_mark.shape[1])/(block_8x8_col*block_8x8_row))
    #矩阵中对角线对称，相对称的互相的大和小代表了黑和白
    #收集关于对角线对称的点
    xydict=findpoint((3,4,-1),r)
    #print(xydict)
    #像素点生成器
    fpgij = fpg(result_mark)
    flag=0
    for i in range(block_8x8_row):
        if(flag):
            break
        for j in range(block_8x8_col):
            if(flag):
                break
            #8*8的块进行DCT变化
            block_8x8_dct=cv.dct(pic_YUV_float32[8*i:8*i+8,8*j:8*j+8,0])
            #忽略8*8的块
            if(block_8x8_dct.shape[0]<8 or block_8x8_dct.shape[1]<8):
                continue
            #遍历8*8里面的像素点
            for point in range(r):
                if(flag):
                    break
                fpg_i,fpg_j=next(fpgij)
                if fpg_i==-1 and fpg_j==-1:
                    flag=1
                point_x,point_y=xydict[point]
                #它对应的中心对称格子
                point_dot=block_8x8_dct[point_x,point_y]
                point_symdot=block_8x8_dct[7-point_x,7-point_y]
                detat=abs(point_dot-point_symdot)
                p=float(detat+1)#0.5用来控制差值
                if result_mark[fpg_i,fpg_j]==0:#表示黑色，用point_dot>point_symdot记录
                    if(point_dot<=point_symdot):
                        block_8x8_dct[point_x,point_y]+=p
                else:#白色则用point_dot<point_symdot记录
                    if(point_dot>=point_symdot):
                        block_8x8_dct[7-point_x,7-point_y]+=p
                if not flag:
                    count+=1
            #逆变换存像素
            water_mark[8*i:8*i+8,8*j:8*j+8,0]=cv.idct(block_8x8_dct)
            #block_water_mark[8*i:8*i+8,8*j:8*j+8,0]=water_mark[8*i:8*i+8,8*j:8*j+8,0]
            #给8*8划线
            # if(block_water_mark.shape[0]>8*i+7)&(block_water_mark.shape[1]>8*j+7):
            #     block_water_mark[8*i:8*i+8,8*j+7,0]=100
            #     block_water_mark[8*i+7,8*j:8*j+8,0]=100
    water_mark_rgb=cv.cvtColor(water_mark.astype('uint8'),cv.COLOR_YUV2RGB)
    # cv.imshow('block_water_mark',cv.cvtColor(block_water_mark.astype('uint8'),cv.COLOR_YUV2RGB))
    # cv.waitKey(0)
    cv.imwrite('after_mark_dct.jpg',water_mark_rgb,[int(cv.IMWRITE_JPEG_QUALITY),100])
    #print(count)

def get_mark(water_mark_path,mark_path):
    water_mark_rgb=cv.imread(water_mark_path)
    water_mark_YUV=cv.cvtColor(water_mark_rgb,cv.COLOR_RGB2YUV)
    water_mark_float=water_mark_YUV.astype('float32')
    block_8x8_row=int(water_mark_float.shape[0]/8)
    block_8x8_col=int(water_mark_float.shape[1]/8)
    r=7
    mark_point_num=187
    extract_xydict=findpoint((3,4,-1),r)
    finish_water_mark=np.zeros([mark_point_num,mark_point_num,3],np.uint8)
    count=0
    point_i=0
    point_j=0
    for i in range(block_8x8_row):
        for j in range(block_8x8_col):
            block_8x8_dct=cv.dct(water_mark_float[8*i:8*i+8,8*j:8*j+8,0])
            if block_8x8_dct.shape[0]<8 or block_8x8_dct.shape[1]<8:
                continue
            for point in range(r):
                if point_i==mark_point_num:
                    break
                point_x, point_y = extract_xydict[point]
                point_dot = block_8x8_dct[point_x, point_y]
                point_symdot = block_8x8_dct[7 - point_x, 7 - point_y]
                if point_dot>=point_symdot:
                    finish_water_mark[point_i,point_j]=0#黑色
                else:
                    if point_dot<point_symdot:
                        finish_water_mark[point_i,point_j]=255
                point_j+=1
                if(point_j==mark_point_num):
                    point_i+=1
                    point_j=0
                count+=1
    cv.imwrite(mark_path, finish_water_mark, [int(cv.IMWRITE_JPEG_QUALITY), 100])

#函数目的是从对角线开始即中频区域找像素点
def findpoint(df,r):
    maxrow,maxcol=8,8
    #dire=-1向右上,dire=1向左下
    di={-1:(-1,1),1:(1,-1)}
    xydict={}
    while(r):
        x,y,dire=df[0],df[1],df[2]
        #边界
        if x==-1:
            df=(0,y-2,1)
            continue
        if y==-1:
            df=(x-2,0,-1)
            continue
        if x==maxrow:
            df=(maxrow-1,y+2,-1)
            continue
        if y==maxcol:
            df=(x+2,maxcol-1,1)
            continue
        r=r-1
        xydict[r]=(x,y)
        dx,dy=x+di[dire][0],y+di[dire][1]
        df=(dx,dy,dire)
    return xydict

def fpg(bsrc):
    for i in range(bsrc.shape[0]):
        for j in range(bsrc.shape[1]):
            yield (i,j)
    while True:#让生成器不会报没东西返回的错
        yield (-1,-1)
    return



insert_watermark("F:\\digital_watermark\\digital-watermark\\Lenna.png","F:\\digital_watermark\\digital-watermark\\digital_mark.png",0)
get_mark("after_mark_dct.jpg","get_mark_dct.jpg")
