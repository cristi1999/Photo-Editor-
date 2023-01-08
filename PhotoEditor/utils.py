from cv2 import cv2
import numpy as np
from scipy.interpolate import UnivariateSpline


# sigma_s controls how much the image is smoothed - the larger its value, the more smoothed the image gets,
# but it's also slower to compute.

# sigma_r is important if you want to preserve edges while smoothing the image. Small sigma_r results in only very
# similar colors to be averaged (i.e. smoothed), while colors that differ much will stay intact.

# function to adjust brightness and contrast
def adjust_brightness_contrast(img, alpha=1, beta=0):
    # contrast from 0 to 3, brightness from -100 to 100
    return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)


# function to adjust saturation
def change_saturation(img, value):
    # -300 to 300
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype("float32")
    (h, s, v) = cv2.split(img_hsv)
    s += value
    s = np.clip(s, 0, 255)
    img_hsv = cv2.merge([h, s, v])
    return cv2.cvtColor(img_hsv.astype("uint8"), cv2.COLOR_HSV2BGR)


# greyscale filter
def greyscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# sharpen filter
def sharpen(img):
    kernel = np.array([[-1, -1, -1], [-1, 9.5, -1], [-1, -1, -1]])
    return cv2.filter2D(img, -1, kernel)


# gaussian blur filter
def gaussian_blur(img):
    return cv2.GaussianBlur(img, (5, 5), 0)


# median blur filter
def median_blur(img):
    return cv2.medianBlur(img, 5)


# cartoon filter
def cartoon(img, sigma_s=64, sigma_r=0.25):
    edges1 = cv2.bitwise_not(cv2.Canny(img, 100, 200))
    dst = cv2.edgePreservingFilter(img, flags=2, sigma_s=sigma_s, sigma_r=sigma_r)
    return cv2.bitwise_and(dst, dst, mask=edges1)


# sepia filter
def sepia(img):
    img_sepia = np.array(img, dtype=np.float64)
    img_sepia = cv2.transform(img_sepia, np.matrix([[0.272, 0.534, 0.131],
                                                    [0.349, 0.686, 0.168],
                                                    [0.393, 0.769,
                                                     0.189]]))
    img_sepia[np.where(img_sepia > 255)] = 255
    img_sepia = np.array(img_sepia, dtype=np.uint8)
    return img_sepia


# pencil sketch grey filter
def pencil_sketch_grey(img, sigma_s=60, sigma_r=0.07):
    sk_gray, sk_color = cv2.pencilSketch(img, sigma_s=sigma_s, sigma_r=sigma_r, shade_factor=0.1)
    return sk_gray


# pencil sketch color filter
def pencil_sketch_color(img, sigma_s=60, sigma_r=0.07):
    sk_gray, sk_color = cv2.pencilSketch(img, sigma_s=sigma_s, sigma_r=sigma_r, shade_factor=0.1)
    return sk_color


# HDR filter
def HDR(img, sigma_s=12, sigma_r=0.15):
    return cv2.detailEnhance(img, sigma_s=sigma_s, sigma_r=sigma_r)


# invert filter
def invert(img):
    return cv2.bitwise_not(img)


def LookupTable(x, y):
    spline = UnivariateSpline(x, y)
    return spline(range(256))


# summer effect filter
def summer_effect(img):
    increase_lookup_table = LookupTable([0, 64, 128, 256], [0, 80, 160, 256])
    decrease_lookup_table = LookupTable([0, 64, 128, 256], [0, 50, 100, 256])
    blue_channel, green_channel, red_channel = cv2.split(img)
    red_channel = cv2.LUT(red_channel, increase_lookup_table).astype(np.uint8)
    blue_channel = cv2.LUT(blue_channel, decrease_lookup_table).astype(np.uint8)
    return cv2.merge((blue_channel, green_channel, red_channel))


# winter effect filter
def winter_effect(img):
    increase_lookup_table = LookupTable([0, 64, 128, 256], [0, 80, 160, 256])
    decrease_lookup_table = LookupTable([0, 64, 128, 256], [0, 50, 100, 256])
    blue_channel, green_channel, red_channel = cv2.split(img)
    red_channel = cv2.LUT(red_channel, decrease_lookup_table).astype(np.uint8)
    blue_channel = cv2.LUT(blue_channel, increase_lookup_table).astype(np.uint8)
    return cv2.merge((blue_channel, green_channel, red_channel))


# save image function
def save_img(img, file):
    cv2.imwrite(file, img)


# rotate image function
def rotate(img):
    return cv2.rotate(img, rotateCode=0)


# crop image function
def crop_img(img, left, right, top, bottom):
    return img[left:right, top:bottom]


# resize image function
def resize_image(img, size=(260, 260)):
    h, w = img.shape[:2]
    c = img.shape[2] if len(img.shape) > 2 else 1
    if h == w:
        return cv2.resize(img, size, cv2.INTER_AREA)
    dif = h if h > w else w
    interpolation = cv2.INTER_AREA if dif > (size[0] + size[1]) // 2 else cv2.INTER_CUBIC
    x_pos = (dif - w) // 2
    y_pos = (dif - h) // 2
    if len(img.shape) == 2:
        mask = np.zeros((dif, dif), dtype=img.dtype)
        mask[y_pos:y_pos + h, x_pos:x_pos + w] = img[:h, :w]
    else:
        mask = np.zeros((dif, dif, c), dtype=img.dtype)
        mask[y_pos:y_pos + h, x_pos:x_pos + w, :] = img[:h, :w, :]
    return cv2.resize(mask, size, interpolation)
