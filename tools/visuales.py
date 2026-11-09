"""Ilustraciones genéricas propias para las historias (sin logos ni arte oficial).

dibujar(tipo, alto, sello=None) -> Image RGBA
  tipo: "slab"  carta gradeada en su funda rígida (etiqueta en blanco, sin marca)
        "carta" carta suelta con marco genérico
        "sobre" sobre/booster con bordes dentados
  sello: palabra corta opcional estampada en diagonal (p. ej. "FALSO", "1/1", "RÉCORD")
"""
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont

F = "/usr/share/fonts/truetype/google-fonts/"
GOLD = (226, 184, 92)
LAV = (196, 170, 255)
WHITE = (245, 242, 255)
S = 3  # supersampling


def _grad(w, h, top, bottom):
    g = Image.new("RGBA", (w, h))
    px = g.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)) + (255,)
        for x in range(w):
            px[x, y] = c
    return g


def _carta(w, h):
    """Carta genérica: marco, ventana de ilustración con brillo y líneas de texto."""
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=int(w * 0.06), fill=255)
    c.paste(_grad(w, h, (52, 28, 98), (20, 12, 40)), (0, 0), mask)
    d = ImageDraw.Draw(c)
    lw = max(2, w // 70)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=int(w * 0.06), outline=LAV + (255,), width=lw)
    m = int(w * 0.08)
    # ventana de ilustración
    ax0, ay0, ax1, ay1 = m, int(h * 0.12), w - m, int(h * 0.58)
    art = _grad(ax1 - ax0, ay1 - ay0, (120, 80, 210), (40, 20, 90))
    c.paste(art, (ax0, ay0))
    # destello diagonal
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.polygon([(ax0 + (ax1 - ax0) * 0.25, ay0), (ax0 + (ax1 - ax0) * 0.45, ay0),
                (ax0 + (ax1 - ax0) * 0.15, ay1), (ax0 - (ax1 - ax0) * 0.05, ay1)], fill=(255, 255, 255, 60))
    clip = Image.new("L", (w, h), 0)
    ImageDraw.Draw(clip).rectangle([ax0, ay0, ax1, ay1], fill=255)
    c.alpha_composite(Image.composite(sh, Image.new("RGBA", (w, h), (0, 0, 0, 0)), clip))
    d.rectangle([ax0, ay0, ax1, ay1], outline=GOLD + (230,), width=lw)
    # barra de nombre y líneas de texto
    d.rounded_rectangle([m, int(h * 0.04), w - m, int(h * 0.09)], radius=lw * 2, fill=LAV + (90,))
    for i, frac in enumerate([0.66, 0.74, 0.82]):
        x1 = w - m - (i % 2) * int(w * 0.18)
        d.rounded_rectangle([m, int(h * frac), x1, int(h * frac) + lw * 3], radius=lw, fill=WHITE + (70,))
    return c


def _slab(w, h):
    s = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    lw = max(3, w // 60)
    r = int(w * 0.07)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=(255, 255, 255, 28), outline=LAV + (255,), width=lw)
    # etiqueta en blanco (sin marca ni nota)
    pad = int(w * 0.07)
    ly0, ly1 = pad, int(h * 0.2)
    d.rounded_rectangle([pad, ly0, w - pad, ly1], radius=lw * 2, fill=(255, 255, 255, 40), outline=GOLD + (255,), width=lw)
    for i, frac in enumerate([0.38, 0.62]):
        yy = ly0 + (ly1 - ly0) * frac
        d.rounded_rectangle([pad * 2, yy - lw, w - pad * 2 - i * int(w * 0.2), yy + lw], radius=lw, fill=GOLD + (170,))
    # ventana interior con la carta
    wx0, wy0, wx1, wy1 = pad, ly1 + pad // 2, w - pad, h - pad
    d.rounded_rectangle([wx0, wy0, wx1, wy1], radius=lw * 2, outline=LAV + (150,), width=max(2, lw // 2))
    cw = int((wx1 - wx0) * 0.84)
    ch = int(cw * 1.4)
    if ch > (wy1 - wy0) * 0.92:
        ch = int((wy1 - wy0) * 0.92)
        cw = int(ch / 1.4)
    s.alpha_composite(_carta(cw, ch), ((w - cw) // 2, wy0 + ((wy1 - wy0) - ch) // 2))
    return s


def _sobre(w, h):
    p = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    teeth = 14
    tooth = int(h * 0.025)
    pts = []
    for i in range(teeth + 1):
        pts.append((w * i / teeth, 0 if i % 2 == 0 else tooth))
    for i in range(teeth, -1, -1):
        pts.append((w * i / teeth, h if i % 2 == 0 else h - tooth))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    p.paste(_grad(w, h, (110, 60, 200), (30, 14, 60)), (0, 0), mask)
    d = ImageDraw.Draw(p)
    lw = max(3, w // 60)
    d.polygon(pts, outline=LAV + (255,))
    d.line([(0, int(h * 0.09)), (w, int(h * 0.09))], fill=GOLD + (220,), width=lw)
    d.line([(0, int(h * 0.91)), (w, int(h * 0.91))], fill=GOLD + (220,), width=lw)
    # brillo
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(w * 0.55, 0), (w * 0.75, 0), (w * 0.35, h), (w * 0.15, h)], fill=(255, 255, 255, 45))
    p.alpha_composite(Image.composite(sh, Image.new("RGBA", (w, h), (0, 0, 0, 0)), mask))
    # carta asomando en el centro
    cw = int(w * 0.5)
    ch = int(cw * 1.4)
    p.alpha_composite(_carta(cw, ch), ((w - cw) // 2, (h - ch) // 2))
    return p


def _sello(img, texto):
    w, h = img.size
    f = ImageFont.truetype(F + "Poppins-Bold.ttf", int(w * 0.27))
    tw = int(ImageDraw.Draw(img).textlength(texto, font=f))
    pad = int(w * 0.05)
    lay = Image.new("RGBA", (tw + pad * 4, int(w * 0.27 * 1.55) + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    lw = max(4, w // 45)
    d.rounded_rectangle([lw, lw, lay.width - lw, lay.height - lw], radius=pad, outline=GOLD + (255,), width=lw)
    d.text((pad * 2, pad * 0.6), texto, font=f, fill=GOLD + (255,))
    lay = lay.rotate(14, expand=True, resample=Image.BICUBIC)
    if lay.width > w * 1.3:
        k = w * 1.3 / lay.width
        lay = lay.resize((int(lay.width * k), int(lay.height * k)), Image.LANCZOS)
    out = Image.new("RGBA", (max(w, lay.width), h), (0, 0, 0, 0))
    out.alpha_composite(img, ((out.width - w) // 2, 0))
    out.alpha_composite(lay, ((out.width - lay.width) // 2, int(h * 0.5 - lay.height / 2)))
    return out


def dibujar(tipo, alto, sello=None):
    H = alto * S
    if tipo == "slab":
        base = _slab(int(H * 0.62), H)
    elif tipo == "sobre":
        base = _sobre(int(H * 0.66), H)
    else:
        base = _carta(int(H / 1.4), H)
    if sello:
        base = _sello(base, sello.upper())
    # halo lavanda detrás
    pad = 40 * S
    out = Image.new("RGBA", (base.width + pad * 2, base.height + pad * 2), (0, 0, 0, 0))
    glow = Image.new("RGBA", out.size, (0, 0, 0, 0))
    a = base.split()[3].point(lambda v: 110 if v > 0 else 0)
    glow.paste(Image.new("RGBA", base.size, (150, 110, 255, 255)), (pad, pad), a)
    out.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18 * S)))
    out.alpha_composite(base, (pad, pad))
    return out.resize((out.width // S, out.height // S), Image.LANCZOS)
