import cv2
import numpy as np
from skimage.color import rgb2lab, deltaE_ciede2000
from sklearn.cluster import KMeans

def visualize_color_diff(img1, img2, delta_thresh=12, k=3, spacer=50):
    h, w = min(img1.shape[0], img2.shape[0]), min(img1.shape[1], img2.shape[1])
    img1, img2 = img1[:h, :w], img2[:h, :w]

    lab1 = rgb2lab(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB) / 255.0)
    lab2 = rgb2lab(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB) / 255.0)
    delta = deltaE_ciede2000(lab1, lab2)
    mask = (delta > delta_thresh).astype(np.uint8)

    coords = np.where(mask.ravel() == 1)[0]
    pixels = img1.reshape(-1, 3)[coords].astype(float)
    if len(pixels) > k:
        km = KMeans(n_clusters=k, random_state=1).fit(pixels)
        centers = km.cluster_centers_.astype(int)
    else:
        centers = np.unique(pixels, axis=0).astype(int)
    hexes = ["#{:02X}{:02X}{:02X}".format(*c[::-1]) for c in centers]

    spacer_img = np.full((h, spacer, 3), 100, np.uint8)
    canvas = np.hstack((img1, spacer_img, img2))

    red = np.zeros_like(img1)
    red[:, :, 2] = 255
    mask3 = np.stack([mask] * 3, axis=-1)

    overlay1 = img1.copy()
    overlay1[mask3 == 1] = cv2.addWeighted(img1, 0.6, red, 0.4, 0)[mask3 == 1]

    overlay2 = img2.copy()
    overlay2[mask3 == 1] = cv2.addWeighted(img2, 0.6, red, 0.4, 0)[mask3 == 1]

    canvas[:, :w] = overlay1
    canvas[:, w + spacer:] = overlay2

    font = cv2.FONT_HERSHEY_SIMPLEX
    fs, ft = 1.0, 2
    pos1 = (10, 30)
    pos2 = (w + spacer + 10, 30)

    cv2.putText(canvas, "Image1", pos1, font, fs, (0, 0, 0), ft + 2, cv2.LINE_AA)
    cv2.putText(canvas, "Image1", pos1, font, fs, (255, 255, 255), ft, cv2.LINE_AA)
    cv2.putText(canvas, "Image2", pos2, font, fs, (0, 0, 0), ft + 2, cv2.LINE_AA)
    cv2.putText(canvas, "Image2", pos2, font, fs, (255, 255, 255), ft, cv2.LINE_AA)

    sw_h = h // (len(centers) + 1)
    for i, c in enumerate(centers):
        x = w + sw_h // 2
        y = sw_h * (i + 1)
        cv2.rectangle(canvas, (x, y), (x + sw_h, y + sw_h), tuple(int(v) for v in c), -1)
        cv2.putText(canvas, hexes[i], (x, y + sw_h + 20), font, 0.7, (255, 255, 255), 1, cv2.LINE_AA)

    return canvas
