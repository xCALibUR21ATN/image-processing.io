import cv2
import numpy as np
from skimage.color import rgb2lab, deltaE_ciede2000
from sklearn.cluster import KMeans

def rgb_to_cmyk(rgb):
    r, g, b = rgb / 255.0
    k = 1 - max(r, g, b)
    if k == 1:
        return 0, 0, 0, 1
    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)
    return c, m, y, k


def visualize_color_diff(img1, img2,img1_n, img2_n, k=3, spacer=50, delta_thresh=12):
    h, w = min(img1.shape[0], img2.shape[0]), min(img1.shape[1], img2.shape[1])
    img1, img2 = img1[:h, :w], img2[:h, :w]

    pixels1 = img1.reshape(-1, 3).astype(float)
    km1 = KMeans(n_clusters=k, random_state=1).fit(pixels1)
    centers1 = km1.cluster_centers_.astype(int)
    lab_centers1 = rgb2lab(np.array([c[::-1] for c in centers1]) / 255.0)

    img2_rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
    lab_img2 = rgb2lab(img2_rgb / 255.0).reshape(-1, 3)
    min_deltaE = np.min([deltaE_ciede2000(lab_img2, np.tile(lab_c, (lab_img2.shape[0], 1)))
                         for lab_c in lab_centers1], axis=0)
    mask = (min_deltaE > delta_thresh).reshape(h, w)

    red = np.zeros_like(img2)
    red[:, :, 2] = 255
    overlay2 = img2.copy()
    mask3 = np.stack([mask] * 3, axis=-1)
    overlay2[mask3 == 1] = cv2.addWeighted(img2, 0.6, red, 0.4, 0)[mask3 == 1]

    spacer_img = np.full((h, spacer, 3), 100, np.uint8)
    canvas = np.hstack((img1, spacer_img, overlay2))

    font = cv2.FONT_HERSHEY_SIMPLEX
    fs, ft = 1.0, 2
    pos1 = (10, 30)
    pos2 = (w + spacer + 10, 30)
    cv2.putText(canvas, f"{img1_n}", pos1, font, fs, (0, 0, 0), ft + 2, cv2.LINE_AA)
    cv2.putText(canvas, f"{img1_n}", pos1, font, fs, (255, 255, 255), ft, cv2.LINE_AA)
    cv2.putText(canvas, f"{img2_n}", pos2, font, fs, (0, 0, 0), ft + 2, cv2.LINE_AA)
    cv2.putText(canvas, f"{img2_n}", pos2, font, fs, (255, 255, 255), ft, cv2.LINE_AA)

    hexes = ["#{:02X}{:02X}{:02X}".format(*c[::-1]) for c in centers1]
    sw_h = h // (len(centers1) + 1)
    for i, c in enumerate(centers1):
        x = w // 2 - sw_h // 2
        y = sw_h * (i + 1)
        color_tuple = tuple(int(v) for v in c)
        cmyk = rgb_to_cmyk(np.array(c[::-1]))
        cmyk_str = "C:{:.0%} M:{:.0%} Y:{:.0%} K:{:.0%}".format(*cmyk)
        # cv2.putText(canvas, cmyk_str, (x, y - 26), font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        # cv2.putText(canvas, hexes[i], (x, y - 10), font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.rectangle(canvas, (x, y), (x + sw_h, y + sw_h), color_tuple, -1)

        text_x = x + 5
        text_y_cmyk = y + sw_h // 3
        text_y_hex = y + (2 * sw_h) // 3 + 6
        cv2.putText(canvas, cmyk_str, (text_x, text_y_cmyk), font, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(canvas, hexes[i], (text_x, text_y_hex), font, 0.55, (255, 255, 255), 1, cv2.LINE_AA)

    return canvas
