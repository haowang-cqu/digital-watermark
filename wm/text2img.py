from PIL import Image,ImageFont,ImageDraw
import os

basedir = os.path.split(os.path.realpath(__file__))[0]

fonts = {
    'SimSun': basedir + '/fonts/simsun.ttc', 
    'SimHei': basedir + '/fonts/simhei.ttf',
    'SimKai': basedir + '/fonts/simkai.ttf',
    'Microsoft YaHei': basedir + '/fonts/msyh.ttc'
}

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


def text2img(text, size, mode='1', fontname='SimSun', fontsize=30):
    """文本转图像
    mode='1' 二值图
    mode='RGB' RGB图
    """
    if fontname not in fonts:
        fontname = 'SimSun'
    font = ImageFont.truetype(fonts[fontname], fontsize)
    lines = textwrap(text, size, font)
    if mode == '1':
        img = Image.new(mode, (size, size), 0)
        dr = ImageDraw.Draw(img)
        y = 0
        for line in lines:
            dr.text((0, y), line, font=font, fill=1)
            y += 1.5 * fontsize # 1.5 倍行距
        return img
    elif mode == 'RGB':
        img = Image.new(mode, (size, size), (0, 0, 0))
        dr = ImageDraw.Draw(img)
        y = 0
        for line in lines:
            dr.text((0, y), line, font=font, fill='#FFFFFF')
            y += 1.5 * fontsize  # 1.5 倍行距
        return img
    else:
        return None
    

if __name__=='__main__':
    img = text2img(u"中文字符1234567890ABCDEFGHIJKLMNabcdefghijklmn", 300, mode='RGB', fontname='aaa', fontsize=50)
    img.show()