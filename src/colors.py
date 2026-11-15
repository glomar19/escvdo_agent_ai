import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

PALETTE = {
    "black": (25, 25, 25), "white": (240, 240, 240), "cream": (245, 238, 215),
    "grey": (128, 128, 128), "beige": (215, 190, 160), "brown": (110, 70, 45),
    "red": (190, 30, 40), "pink": (240, 160, 180), "orange": (230, 120, 40),
    "yellow": (235, 200, 60), "lime": (170, 185, 60), "green": (60, 130, 70),
    "blue": (50, 100, 190), "navy": (20, 30, 90), "purple": (110, 60, 150),
    "light pink": (245, 215, 225), "light yellow": (245, 235, 160),
    "light blue": (190, 215, 240),
}
REGIONS = {"upper": (0.25, 0.55), "lower": (0.55, 0.90), "all": (0.15, 0.85)}

def nearest_color(rgb):
    return min(PALETTE, key=lambda n: sum((a - b) ** 2 for a, b in zip(PALETTE[n], rgb)))

def dominant_color(image_path, k=3, region="all", tol=40):
    img = Image.open(image_path).convert("RGB").resize((120, 160))
    a = np.array(img).astype(float)
    h, w, _ = a.shape

    # color de fondo en cada fila: mediana de los bordes izquierdo y derecho
    edge = np.concatenate([a[:, :int(w * 0.12)], a[:, int(w * 0.88):]], axis=1)
    bg = np.median(edge, axis=1)                      # (h, 3)

    y0, y1 = REGIONS[region]
    ys, xs = slice(int(h * y0), int(h * y1)), slice(int(w * 0.30), int(w * 0.70))
    crop = a[ys, xs]
    dist = np.linalg.norm(crop - bg[ys][:, None, :], axis=2)

    px = crop.reshape(-1, 3)[(dist > tol).reshape(-1)]   # quita el fondo
    if len(px) < 50:                                     # prenda casi igual al fondo
        px = crop.reshape(-1, 3)

    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(px)
    main = km.cluster_centers_[np.bincount(km.labels_).argmax()]
    return nearest_color(main), tuple(int(x) for x in main)