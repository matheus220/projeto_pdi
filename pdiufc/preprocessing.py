import numpy as np
import cv2


def process(image):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    sat = img[:, :, 1]

    med = cv2.medianBlur(sat, 5)

    blur = cv2.blur(med, (5, 5))

    ret, th_img = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    th_img_blur = cv2.medianBlur(th_img, 5)

    # imfill process

    im_floodfill = th_img_blur.copy()

    # Mask used to flood filling.
    # Notice the size needs to be 2 pixels than the image.
    h, w = th_img_blur.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)

    # Floodfill from point (0, 0)
    cv2.floodFill(im_floodfill, mask, (0, 0), 255)

    # Invert floodfilled image
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)

    # Combine the two images to get the foreground.
    im_out = th_img_blur | im_floodfill_inv

    return im_out
