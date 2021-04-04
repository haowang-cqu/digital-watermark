from PIL import Image,ImageFont,ImageDraw
import os

basedir = os.path.split(os.path.realpath(__file__))[0]

def textwrap(text, width, font):
    """文本换行
    """
    lines = ['']
    temp = width
    for c in text:
        w, _ = font.getsize(c)
        if temp < w:
            temp = width
            lines.append('')
        lines[-1] += c
        temp -= w
    return lines


def text2img(text, width, height, mode='1', fontsize=30):
    """文本转二值图
    mode='1' 二值图
    mode='RGB' RGB图
    """
    font = ImageFont.truetype(basedir + "/fonts/YaHei Consolas Hybrid 1.12.ttf", fontsize)
    lines = textwrap(text, width, font)
    if mode == '1':
        img = Image.new(mode, (width, height), 0)
        dr = ImageDraw.Draw(img)
        y = 0
        for line in lines:
            dr.text((0, y), line, font=font, fill=1)
            y += 1.5 * fontsize # 1.5 倍行距
        return img
    elif mode == 'RGB':
        img = Image.new(mode, (width, height), (0, 0, 0))
        dr = ImageDraw.Draw(img)
        y = 0
        for line in lines:
            dr.text((0, y), line, font=font, fill='#FFFFFF')
            y += 1.5 * fontsize  # 1.5 倍行距
        return img
    else:
        return None
    

if __name__=='__main__':
    img = text2img(u"中文字符1234567890ABCDEFGHIJKLMNabcdefghijklmn", 300, 300, mode='RGB', fontsize=50)
    img.show()