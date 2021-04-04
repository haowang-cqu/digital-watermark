import numpy as np
from PIL import Image


def arnold_encode(image, shuffle_times=5, a=1234, b=1234, mode='1'):
    """ Arnold 置乱
    """
    image = np.array(image)
    arnold_image = np.zeros(shape=image.shape, dtype=image.dtype)
    h, w = image.shape[0], image.shape[1]
    N = h
    for _ in range(shuffle_times):
        for ori_x in range(h):
            for ori_y in range(w):
                new_x = (1*ori_x + b*ori_y)% N
                new_y = (a*ori_x + (a*b+1)*ori_y) % N
                if mode == '1':
                    arnold_image[new_x, new_y] = image[ori_x, ori_y]
                else:
                    arnold_image[new_x, new_y, :] = image[ori_x, ori_y, :]
    return Image.fromarray(arnold_image)


def arnold_decode(image, shuffle_times=5, a=1234, b=1234, mode='1'):
    """ 恢复 Arnold 置乱
    """
    image = np.array(image)
    decode_image = np.zeros(shape=image.shape, dtype=image.dtype)
    h, w = image.shape[0], image.shape[1]
    N = h
    for _ in range(shuffle_times):
        for ori_x in range(h):
            for ori_y in range(w):
                new_x = ((a*b+1)*ori_x + (-b)* ori_y)% N
                new_y = ((-a)*ori_x + ori_y) % N
                if mode == '1':
                    decode_image[new_x, new_y] = image[ori_x, ori_y]
                else:
                    decode_image[new_x, new_y, :] = image[ori_x, ori_y, :]
    return Image.fromarray(decode_image)


if __name__=='__main__':
    from wm.text2img import text2img
    img = text2img(u'测试图像', 300, mode='1', fontsize=50)
    img.save('temp/before.png')
    encode_img = arnold_encode(img)
    encode_img.save('temp/encode.png')
    decode_img = arnold_decode(encode_img)
    decode_img.save('temp/after.png')
