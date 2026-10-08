import cv2, numpy as np
img = cv2.imread('fachada.png'); h, w = img.shape[:2]
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV); gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(int)
b, g, r = [img[..., i].astype(int) for i in range(3)]
zona = np.zeros((h, w), np.uint8)
top = [(150, 138), (322, 92), (430, 148), (700, 112), (905, 78)]
bot = [(905, 300 - 8), (150, 370 - 8)]
cv2.fillPoly(zona, [np.array(top + [(905, 215), (395, 300), (400, 337), (150, 362)], np.int32)], 255)
# no tocar la lámpara junto a la línea superior
cv2.circle(zona, (230, 101), 9, 0, -1)
pared = np.median(gray[zona > 0])
claro = gray > pared + 14
rojo = (hsv[..., 1] > 80) & ((hsv[..., 0] < 12) | (hsv[..., 0] > 165))
calido = ((r - b) > 10) & (gray > pared + 5)
mask = ((claro | rojo | calido) & (zona > 0)).astype(np.uint8) * 255
mask = cv2.dilate(mask, np.ones((7, 7), np.uint8), iterations=3)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
mask = cv2.bitwise_and(mask, zona)
# todo el engranaje viejo (incluye su halo bajo)
cv2.fillPoly(mask, [np.array([(165,150),(250,112),(330,100),(370,150),(372,330),(330,352),(165,362)], np.int32)], 255)
cv2.circle(mask, (230, 101), 10, 0, -1)
cv2.imwrite('mask.png', mask)
limpio = cv2.inpaint(img, mask, 15, cv2.INPAINT_NS)
blur = cv2.GaussianBlur(limpio, (0, 0), 12)
m3 = cv2.GaussianBlur(mask, (0, 0), 5).astype(np.float32)[..., None] / 255
out = limpio * (1 - m3) + blur * m3
out = np.clip(out + np.random.default_rng(1).normal(0, 2.0, out.shape) * m3, 0, 255).astype(np.uint8)
cv2.imwrite('limpio.png', out)
