import numpy as np
from PIL import Image
def get_RGB(pic_path,mark_path):
    mark=Image.open(mark_path)
    pic=Image.open(pic_path)
    #先转换为黑白
    mark=mark.convert("L")
    #转换成RGB格式
    mark=mark.convert("RGB")
    pic=pic.convert("RGB")
    return pic,mark

def LSB_encode(pic,mark):
    for i in range(mark.size[0]):
        for j in range(mark.size[1]):
            rgb = pic.getpixel((i, j))
            r=rgb[0]
            g=rgb[1]
            b=rgb[2]
            if mark.getpixel((i,j))==(255,255,255):
                b=b-b%2+1
            elif mark.getpixel((i,j))==(0,0,0):
                b=b-b%2+0
            pic.putpixel((i,j),(r,g,b))
    pic.save("test1.png")

def get_water(pic):
    img=Image.new('RGB',(pic.size[0],pic.size[1]))
    for i in range(pic.size[0]):
        for j in range(pic.size[1]):
            rgb=pic.getpixel((i,j))
            if rgb[2]%2==0:
                img.putpixel((i,j),(0,0,0))
            elif rgb[2]%2==1:
                img.putpixel((i,j),(255,255,255))
    img.save("mark1.png")
pic,mark=get_RGB("./123.jpg","./digital_mark.png")
LSB_encode(pic,mark)
get_water(pic)