import numpy as np
from PIL import Image


def arnold_encode(image, shuffle_times, a, b, mode='1'):
    """ Arnold 置乱
    """
    arnold_image = np.zeros(shape=image.shape)
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
    if mode == '1':
        return arnold_image.astype(np.bool8)
    else:
        return arnold_image.astype(np.uint8)


def arnold_decode(image, shuffle_times, a, b, mode='1'):
    """ 恢复 Arnold 置乱
    """
    decode_image = np.zeros(shape=image.shape)
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
    if mode == '1':
        return decode_image.astype(np.bool8)
    else:
        return decode_image.astype(np.uint8)


if __name__=='__main__':
    shuffle_times, a, b = 5, 1234, 1234
    mode = '1'
    from text2img import text2img
    img = text2img(u'测试图像', 200, 200, mode=mode, fontsize=50)
    img.save('before.png')
    encode_img = arnold_encode(np.array(img), shuffle_times, a, b, mode=mode)
    Image.fromarray(encode_img).save('encode.png')
    decode_img = arnold_decode(encode_img, shuffle_times, a, b, mode=mode)
    Image.fromarray(decode_img).save('after.png')
