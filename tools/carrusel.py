"""Genera un carrusel de Instagram (slides cuadradas 1080x1080) con la estética AREA151.

Uso:
    python3 tools/carrusel.py spec.json

spec.json:
{
  "salida": "carruseles/2026-11-26-gta-vi-panini/",   # carpeta; cada slide sale como 01.jpg, 02.jpg...
  "fuente": "Fuente: Panini America · 24 nov. 2026",  # se pinta en las slides que digan "fuente": true
  "slides": [
    {"fuente": true, "bloques": [
      {"tipo": "etiqueta", "texto": "NOVEDAD PANINI"},     # dorado, espaciado, con línea corta debajo
      {"tipo": "visual", "visual": "sobre", "sello": "1/1", "alto": 250},  # ilustración propia (visuales.py)
      {"tipo": "titulo", "lineas": ["LAS CARTAS", "DE GTA VI"]},            # blanco, grande
      {"tipo": "destacado", "lineas": ["YA SON REALES"]},                  # lavanda
      {"tipo": "ficha", "texto": "GTAVI: Sports Trading Card Collection"}, # dorado mediano
      {"tipo": "texto", "lineas": ["Frase corta.", "Otra frase."]},        # fino, lavanda claro
      {"tipo": "cifras", "items": [["4", "CARTAS", "POR SOBRE"], ...], "cols": 3},  # números grandes en recuadros
      {"tipo": "filas", "items": [["Legend Gold", "1/1"], ...]},           # izquierda blanco, derecha dorado
      {"tipo": "nota", "texto": "Según Panini America."},                  # pequeño, gris lavanda
      {"tipo": "desliza"},                                                 # «DESLIZA» con flecha dibujada
      {"tipo": "hueco", "alto": 20}
    ]}
  ]
}

Reglas de diseño: sin adornos en las esquinas, sin píldoras doradas macizas, sin emojis
(la fuente no los tiene). En la portada el contenido va dentro del ancho central (~820 px)
para que la cuadrícula del perfil (3:4) no lo corte.
"""
import json
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

W = H = 1080
F = "/usr/share/fonts/truetype/google-fonts/"
GOLD = (226, 184, 92)
LAV = (196, 170, 255)
WHITE = (245, 242, 255)
SOFT = (215, 205, 240)
GREY = (170, 160, 200)
TOP, BOTTOM = 70, 975     # zona del contenido
Y_FUENTE, Y_MARCA = 968, 1010


def font(weight, size):
    return ImageFont.truetype(F + f"Poppins-{weight}.ttf", size)


def fit(dr, text, weight, size, max_w, min_size=24):
    while size > min_size and dr.textlength(text, font=font(weight, size)) > max_w:
        size -= 2
    return font(weight, size)


def fondo(seed=151):
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W * 0.5) / W) ** 2 + ((y - H * 0.42) / H) ** 2)
    g = np.clip(1 - d * 1.5, 0, 1) ** 1.8
    base, glow = np.array([8, 5, 16]), np.array([70, 30, 130])
    bg = base + (glow - base) * g[..., None]
    beam = np.clip(1 - np.abs(x - W / 2) / (80 + y * 0.32), 0, 1) * np.clip(1 - y / 900, 0, 1)
    bg += np.array([60, 45, 110]) * (beam ** 2 * 0.3)[..., None]
    img = Image.fromarray(np.clip(bg, 0, 255).astype("uint8"))
    stars = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(stars)
    rnd = random.Random(seed)
    for _ in range(150):
        sx, sy, r = rnd.randint(0, W), rnd.randint(0, H), rnd.choice([1, 1, 1, 2])
        sd.ellipse([sx - r, sy - r, sx + r, sy + r], fill=rnd.randint(60, 170))
    return Image.composite(Image.new("RGB", (W, H), WHITE), img, stars.filter(ImageFilter.GaussianBlur(0.6)))


def espaciado(dr, x_centro, y, texto, f, col, sp):
    widths = [dr.textlength(c, font=f) for c in texto]
    x = x_centro - (sum(widths) + sp * (len(texto) - 1)) / 2
    for c, w in zip(texto, widths):
        dr.text((x, y), c, font=f, fill=col)
        x += w + sp


def centrado(dr, y, texto, f, col):
    dr.text(((W - dr.textlength(texto, font=f)) / 2, y), texto, font=f, fill=col)


def medir(dr, b, max_w):
    """Devuelve (alto, función de pintado) de un bloque."""
    t = b["tipo"]
    if t == "etiqueta":
        txt = b["texto"].upper()
        f = fit(dr, txt, "Medium", 30, max_w - 120)
        def pintar(img, dr, y):
            espaciado(dr, W / 2, y, txt, f, GOLD, 8)
            dr.line([(W / 2 - 50, y + 58), (W / 2 + 50, y + 58)], fill=GOLD, width=3)
        return 58 + 34, pintar
    if t == "hueco":
        return b.get("alto", 20), lambda img, dr, y: None
    if t == "visual":
        from visuales import dibujar
        v = dibujar(b["visual"], b.get("alto", 240), b.get("sello"))
        def pintar(img, dr, y):
            img.paste(v, ((W - v.width) // 2, y - 30), v)
        return v.height - 50, pintar
    if t in ("titulo", "destacado"):
        size0 = b.get("tam", 92 if t == "titulo" else 76)
        col = WHITE if t == "titulo" else LAV
        filas = []
        for ln in b["lineas"]:
            f = fit(dr, ln.upper(), "Bold", size0, max_w, 40)
            filas.append((ln.upper(), f, int(f.size * 1.18)))
        def pintar(img, dr, y):
            for txt, f, lh in filas:
                centrado(dr, y, txt, f, col)
                y += lh
        return sum(r[2] for r in filas), pintar
    if t == "ficha":
        f = fit(dr, b["texto"], "Medium", b.get("tam", 34), max_w, 24)
        return 54, lambda img, dr, y: centrado(dr, y, b["texto"], f, GOLD)
    if t == "texto":
        size = min(fit(dr, ln, "Regular", b.get("tam", 36), max_w, 26).size for ln in b["lineas"])
        f = font("Regular", size)
        lh = int(size * 1.45)
        def pintar(img, dr, y):
            for ln in b["lineas"]:
                centrado(dr, y, ln, f, SOFT)
                y += lh
        return lh * len(b["lineas"]), pintar
    if t == "nota":
        f = fit(dr, b["texto"], "Regular", 24, max_w, 18)
        return 40, lambda img, dr, y: centrado(dr, y, b["texto"], f, GREY)
    if t == "cifras":
        items, cols = b["items"], b.get("cols", len(b["items"]))
        gap = 26
        cw = (max_w - gap * (cols - 1)) // cols
        ch = b.get("alto_caja", 230)
        rows = (len(items) + cols - 1) // cols
        fn = font("Bold", b.get("tam_num", 104))
        def pintar(img, dr, y):
            x0 = (W - (cw * cols + gap * (cols - 1))) // 2
            for i, it in enumerate(items):
                r, c = divmod(i, cols)
                x, yy = x0 + c * (cw + gap), y + r * (ch + gap)
                capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(capa).rounded_rectangle([x, yy, x + cw, yy + ch], radius=22,
                                                       fill=(40, 22, 80, 150), outline=LAV + (200,), width=3)
                img.paste(Image.alpha_composite(img.convert("RGBA"), capa).convert("RGB"))
                dr = ImageDraw.Draw(img)
                num = it[0]
                dr.text((x + (cw - dr.textlength(num, font=fn)) / 2, yy + 12), num, font=fn, fill=GOLD)
                ly = yy + 12 + int(fn.size * 1.12)
                for ln in it[1:]:
                    fl = fit(dr, ln.upper(), "Bold", b.get("tam_txt", 28), cw - 30, 18)
                    dr.text((x + (cw - dr.textlength(ln.upper(), font=fl)) / 2, ly), ln.upper(), font=fl, fill=WHITE)
                    ly += int(fl.size * 1.25)
        return rows * ch + (rows - 1) * gap, pintar
    if t == "filas":
        items = b["items"]
        rh, gap = b.get("alto_fila", 92), 16
        fl = font("Bold", b.get("tam", 36))
        fr = font("Bold", b.get("tam", 36) + 4)
        fs = font("Regular", 24)
        def pintar(img, dr, y):
            x0, x1 = (W - max_w) // 2, (W + max_w) // 2
            for i, it in enumerate(items):
                yy = y + i * (rh + gap)
                capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(capa).rounded_rectangle([x0, yy, x1, yy + rh], radius=18,
                                                       fill=(40, 22, 80, 140), outline=LAV + (170,), width=2)
                img.paste(Image.alpha_composite(img.convert("RGBA"), capa).convert("RGB"))
                dr = ImageDraw.Draw(img)
                izq, der = it[0], it[1]
                sub = it[2] if len(it) > 2 else None
                f_izq = fit(dr, izq, "Bold", fl.size, max_w * 0.62, 22)
                if sub:
                    dr.text((x0 + 30, yy + rh / 2 - f_izq.size * 1.18), izq, font=f_izq, fill=WHITE)
                    f_sub = fit(dr, sub, "Regular", fs.size, max_w * 0.62, 18)
                    dr.text((x0 + 30, yy + rh / 2 + 6), sub, font=f_sub, fill=GREY)
                else:
                    dr.text((x0 + 30, yy + (rh - f_izq.size * 1.35) / 2), izq, font=f_izq, fill=WHITE)
                f_der = fit(dr, der, "Bold", fr.size, max_w * 0.34, 20)
                dr.text((x1 - 30 - dr.textlength(der, font=f_der), yy + (rh - f_der.size * 1.35) / 2), der,
                        font=f_der, fill=GOLD)
        return len(items) * rh + (len(items) - 1) * gap, pintar
    if t == "desliza":
        f = font("Medium", 26)
        def pintar(img, dr, y):
            txt = "DESLIZA"
            widths = [dr.textlength(c, font=f) for c in txt]
            tw = sum(widths) + 6 * (len(txt) - 1)
            x = (W - tw - 50) / 2
            espaciado(dr, x + tw / 2, y, txt, f, LAV, 6)
            ax, ay = x + tw + 18, y + 20
            dr.line([(ax, ay), (ax + 30, ay)], fill=LAV, width=3)
            dr.line([(ax + 20, ay - 9), (ax + 30, ay), (ax + 20, ay + 9)], fill=LAV, width=3, joint="curve")
        return 44, pintar
    raise ValueError(f"bloque desconocido: {t}")


def slide(spec, s, n, total):
    img = fondo(151 + n)
    dr = ImageDraw.Draw(img)
    max_w = s.get("ancho", 860)
    piezas = [medir(dr, b, max_w) for b in s["bloques"]]
    fondo_y = (Y_FUENTE - 20) if s.get("fuente") else BOTTOM - 20
    alto = sum(p[0] for p in piezas)
    y = TOP + max(0, (fondo_y - TOP - alto) // 2)
    for h, pintar in piezas:
        pintar(img, dr, y)
        dr = ImageDraw.Draw(img)
        y += h
    if y > fondo_y:
        print(f"AVISO slide {n}: el contenido llega a y={y} (límite {fondo_y})")
    if s.get("fuente") and spec.get("fuente"):
        ft = fit(dr, spec["fuente"], "Regular", 26, 900, 20)
        centrado(dr, Y_FUENTE - 6, spec["fuente"], ft, GREY)
    # Marca y número de slide
    espaciado(dr, W / 2, Y_MARCA, "AREA151", font("Bold", 34), WHITE, 8)
    return img, y


def main(path):
    spec = json.load(open(path, encoding="utf-8"))
    out = spec["salida"]
    os.makedirs(out, exist_ok=True)
    total = len(spec["slides"])
    for i, s in enumerate(spec["slides"], 1):
        img, y = slide(spec, s, i, total)
        ruta = os.path.join(out, f"{i:02d}.jpg")
        img.save(ruta, quality=93)
        print(ruta, "y_final=", y)


if __name__ == "__main__":
    main(sys.argv[1])
