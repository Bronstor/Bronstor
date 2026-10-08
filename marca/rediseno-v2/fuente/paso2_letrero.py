import cv2, numpy as np
wall = cv2.imread('limpio.png').astype(np.float32)
logo = cv2.imread('logo_flat.png', cv2.IMREAD_UNCHANGED).astype(np.float32)
H0, W0 = logo.shape[:2]
pad = int(H0 * 0.35)
logo = cv2.copyMakeBorder(logo, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
Hp, Wp = logo.shape[:2]
a = logo[..., 3] / 255.0
rgb = logo[..., :3]
# caras: aluminio cepillado (blanco) con degradado vertical; rojo se mantiene
yy = np.linspace(0, 1, Hp)[:, None]
blanco = (rgb.mean(axis=2) > 200)
shade = (1.0 - 0.13 * yy)[..., None]
face = rgb * shade
sf = np.broadcast_to(shade[..., 0], (Hp, Wp)); face[blanco] = np.array([236, 237, 240], np.float32) * sf[blanco][:, None]
# elementos pequeños: a la derecha del símbolo y bajo la palabra -> sin canto
small = np.zeros((Hp, Wp), np.float32)
small[pad + int(H0 * 0.58):, pad + int(H0 * 2.3):] = 1.0
a_big = a * (1 - small)
# canto (extrusión) hacia abajo-izquierda
depth = int(H0 * 0.075)
side = np.zeros_like(rgb); side_a = np.zeros_like(a)
for k in range(depth, 0, -1):
    dx, dy = -int(k * 0.55), int(k * 0.85)
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    ak = cv2.warpAffine(a_big, M, (Wp, Hp))
    ck = cv2.warpAffine(rgb, M, (Wp, Hp))
    tone = np.where((ck.mean(axis=2) > 200)[..., None], np.array([120, 122, 126], np.float32), ck * 0.45)
    side = side * (1 - ak[..., None]) + tone * ak[..., None]
    side_a = np.maximum(side_a, ak)
layer_rgb = side * (1 - a[..., None]) + face * a[..., None]
layer_a = np.maximum(side_a, a)
# halo de retroiluminación
dil = cv2.dilate((layer_a * 255).astype(np.uint8), np.ones((15, 15), np.uint8))
halo = cv2.GaussianBlur(dil.astype(np.float32) / 255, (0, 0), H0 * 0.09)
# homografía hacia la pared (punto de fuga a la izquierda)
VP = np.array([-974.0, 473.0])
xl, xr = 185.0, 860.0
def band(x):
    ys = 125 - 0.31 * (x - 150); yf = 370 - 0.092 * (x - 150); return ys, yf
ys, yf = band(xl)
ytl, ybl = ys + (yf - ys) * 0.42, ys + (yf - ys) * 0.71
def through(x, y0):
    m = (y0 - VP[1]) / (xl - VP[0]); return y0 + m * (x - xl)
ytr, ybr = through(xr, ytl), through(xr, ybl)
# las esquinas del logo plano incluyen el margen: calcular sobre el área sin margen
src = np.float32([[pad, pad], [pad + W0, pad], [pad + W0, pad + H0], [pad, pad + H0]])
dst = np.float32([[xl, ytl], [xr, ytr], [xr, ybr], [xl, ybl]])
Hm = cv2.getPerspectiveTransform(src, dst)
h, w = wall.shape[:2]
L = cv2.warpPerspective(layer_rgb, Hm, (w, h), flags=cv2.INTER_CUBIC)
LA = cv2.warpPerspective(layer_a, Hm, (w, h), flags=cv2.INTER_LINEAR)[..., None]
HA = cv2.warpPerspective(halo, Hm, (w, h), flags=cv2.INTER_LINEAR)[..., None]
warm = np.array([200, 228, 255], np.float32)  # BGR blanco cálido
out = wall + (warm - wall) * np.clip(HA * 0.62, 0, 1) * 0.85
out = out * (1 - LA) + L * LA
# grano de cámara para integrar
out += np.random.default_rng(3).normal(0, 1.6, out.shape) * LA
cv2.imwrite('fachada_EM.png', np.clip(out, 0, 255).astype(np.uint8))
print('ok', dst.tolist())
