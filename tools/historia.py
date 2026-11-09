"""Genera una historia de Instagram (1080x1920) con la estética AREA151.

Uso:
    python3 tools/historia.py spec.json

spec.json:
{
  "etiqueta": "NOVEDAD POKÉMON TCG",          # línea dorada pequeña arriba
  "titulo": ["CUBARSÍ", "NO TIENE"],          # líneas grandes en blanco
  "destacado": ["MASTER ROOKIE"],             # líneas grandes en lavanda (opcional)
  "remate": "EN MEGACRACKS",                  # línea mediana en blanco (opcional)
  "texto": ["Frase corta 1.", "Frase corta 2."],  # 1-3 líneas finas (opcional)
  "salida": "stories/2026-11-09-cubarsi.jpg"
}

Reglas de diseño: todo el contenido entre y=320 y y=1400, sin adornos en las
esquinas, sin píldoras doradas macizas, sin emojis (la fuente no los tiene).
"""
import json
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
F = "/usr/share/fonts/truetype/google-fonts/"
GOLD = (226, 184, 92)
LAV = (196, 170, 255)
WHITE = (245, 242, 255)
SOFT = (215, 205, 240)
MAX_W = 920
TOP, BOTTOM = 360, 1240  # zona del bloque de texto; la marca va en 1300


def font(weight, size):
    return ImageFont.truetype(F + f"Poppins-{weight}.ttf", size)


def fit(draw, text, weight, size, min_size=40):
    while size > min_size and draw.textlength(text, font=font(weight, size)) > MAX_W:
        size -= 2
    return font(weight, size)


def fondo():
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W * 0.5) / W) ** 2 + ((y - H * 0.38) / H * 1.1) ** 2)
    g = np.clip(1 - d * 1.6, 0, 1) ** 1.8
    base, glow = np.array([8, 5, 16]), np.array([70, 30, 130])
    bg = base + (glow - base) * g[..., None]
    beam = np.clip(1 - np.abs(x - W / 2) / (80 + y * 0.32), 0, 1) * np.clip(1 - y / 1500, 0, 1)
    bg += np.array([60, 45, 110]) * (beam ** 2 * 0.35)[..., None]
    img = Image.fromarray(np.clip(bg, 0, 255).astype("uint8"))
    stars = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(stars)
    rnd = random.Random(151)
    for _ in range(220):
        sx, sy, r = rnd.randint(0, W), rnd.randint(0, H), rnd.choice([1, 1, 1, 2])
        sd.ellipse([sx - r, sy - r, sx + r, sy + r], fill=rnd.randint(60, 180))
    return Image.composite(Image.new("RGB", (W, H), WHITE), img, stars.filter(ImageFilter.GaussianBlur(0.6)))


def main(path):
    spec = json.load(open(path, encoding="utf-8"))
    img = fondo()
    dr = ImageDraw.Draw(img)

    # Construir los bloques: (texto, fuente, color, alto de línea, espaciado de letras)
    rows = []
    if spec.get("etiqueta"):
        rows.append((spec["etiqueta"].upper(), fit(dr, spec["etiqueta"].upper(), "Medium", 34), GOLD, 58, 9))
        rows.append(("__linea__", None, GOLD, 82, 0))
    for t in spec.get("titulo", []):
        rows.append((t.upper(), fit(dr, t.upper(), "Bold", 118), WHITE, 138, 0))
    for t in spec.get("destacado", []):
        rows.append((t.upper(), fit(dr, t.upper(), "Bold", 104), LAV, 130, 0))
    if spec.get("remate"):
        rows.append((spec["remate"].upper(), fit(dr, spec["remate"].upper(), "Bold", 64), WHITE, 100, 0))
    texto = spec.get("texto", [])
    if texto:
        rows.append(("__hueco__", None, None, 30, 0))
        for t in texto:
            rows.append((t, fit(dr, t, "Regular", 40, 30), SOFT, 62, 0))

    total = sum(r[3] for r in rows)
    y = TOP + max(0, (BOTTOM - TOP - total) // 2)
    for text, f, col, lh, sp in rows:
        if text == "__linea__":
            dr.line([(W / 2 - 60, y), (W / 2 + 60, y)], fill=col, width=3)
        elif text != "__hueco__":
            if sp:
                widths = [dr.textlength(c, font=f) for c in text]
                x = (W - (sum(widths) + sp * (len(text) - 1))) / 2
                for c, w in zip(text, widths):
                    dr.text((x, y), c, font=f, fill=col)
                    x += w + sp
            else:
                dr.text(((W - dr.textlength(text, font=f)) / 2, y), text, font=f, fill=col)
        y += lh

    # Marca
    mark, f, sp = "AREA151", font("Bold", 46), 10
    widths = [dr.textlength(c, font=f) for c in mark]
    x = (W - (sum(widths) + sp * (len(mark) - 1))) / 2
    for c, w in zip(mark, widths):
        dr.text((x, 1300), c, font=f, fill=WHITE)
        x += w + sp

    img.save(spec["salida"], quality=92)
    print(spec["salida"], "y_final_bloque=", y)


if __name__ == "__main__":
    main(sys.argv[1])
