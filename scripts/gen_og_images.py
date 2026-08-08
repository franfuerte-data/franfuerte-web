"""
Generate branded OpenGraph images (1200x630) for social media previews.
Optimized for WhatsApp, Telegram, LinkedIn, Twitter/X.

Run: python scripts/gen_og_images.py
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), '..', 'public', 'og')
os.makedirs(OUT, exist_ok=True)

W, H = 1200, 630

# Brand palette
BG_DARK = (6, 8, 22)
VIOLET_500 = (139, 92, 246)
VIOLET_300 = (196, 181, 253)
CYAN_400 = (34, 211, 238)
CYAN_300 = (103, 232, 249)
WHITE = (255, 255, 255)
SLATE_400 = (148, 163, 184)
SLATE_300 = (203, 213, 225)


def font(size, weight="regular"):
    """Try to find a decent font. Falls back to default if not available."""
    candidates = []
    if weight == "bold":
        candidates = [
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\calibrib.ttf",
        ]
    elif weight == "black":
        candidates = [
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\Impact.ttf",
        ]
    else:
        candidates = [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\calibri.ttf",
        ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def radial_gradient(size, center, inner_color, outer_color, radius):
    """Create a radial gradient overlay."""
    w, h = size
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    px = img.load()
    cx, cy = center
    for y in range(h):
        for x in range(w):
            dx, dy = x - cx, y - cy
            d = (dx*dx + dy*dy) ** 0.5
            t = min(1.0, d / radius)
            r = int(inner_color[0] * (1-t) + outer_color[0] * t)
            g = int(inner_color[1] * (1-t) + outer_color[1] * t)
            b = int(inner_color[2] * (1-t) + outer_color[2] * t)
            a = int(inner_color[3] * (1-t) + outer_color[3] * t) if len(inner_color) > 3 else 255
            px[x, y] = (r, g, b, a)
    return img


def base_background():
    """Base dark background with subtle radial glows in violet + cyan (brand)."""
    img = Image.new('RGB', (W, H), BG_DARK)
    # Violet glow top-left
    violet_glow = radial_gradient(
        (W, H), (200, 180),
        (*VIOLET_500, 90), (*BG_DARK, 0),
        radius=600,
    )
    # Cyan glow top-right
    cyan_glow = radial_gradient(
        (W, H), (1000, 200),
        (*CYAN_400, 65), (*BG_DARK, 0),
        radius=550,
    )
    img_rgba = img.convert('RGBA')
    img_rgba = Image.alpha_composite(img_rgba, violet_glow)
    img_rgba = Image.alpha_composite(img_rgba, cyan_glow)
    return img_rgba.convert('RGB')


def draw_gradient_text(draw, xy, text, font_obj, color1, color2, img):
    """Draw text with a horizontal gradient (poor-man's version: draw twice with slight offset)."""
    # For simplicity, draw solid — real gradient requires masking
    draw.text(xy, text, fill=color1, font=font_obj)


def draw_pill(draw, xy, text, font_obj, bg=(20, 30, 50, 200), fg=CYAN_300, pad=(14, 8)):
    """Draw a pill/badge."""
    x, y = xy
    tw = draw.textlength(text, font=font_obj)
    th = font_obj.size
    box = (x, y, x + tw + 2*pad[0], y + th + 2*pad[1])
    draw.rounded_rectangle(box, radius=int((th + 2*pad[1]) / 2), fill=bg, outline=(*CYAN_400, 90), width=1)
    draw.text((x + pad[0], y + pad[1] - 2), text, fill=fg, font=font_obj)
    return box


def draw_cert_chip(draw, xy, code, accent_rgb):
    """Draw a certification chip."""
    x, y = xy
    f = font(22, "bold")
    tw = draw.textlength(code, font=f)
    pad_x, pad_y = 16, 8
    w = tw + 2*pad_x
    h = f.size + 2*pad_y + 2
    box = (x, y, x + w, y + h)
    # Semi-transparent bg
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle(box, radius=int(h/2), fill=(*accent_rgb, 40), outline=(*accent_rgb, 200), width=2)
    return overlay, code, f, (x + pad_x, y + pad_y - 2), accent_rgb


# ── Default OG image ──────────────────────────────────────────────────────────

def gen_default():
    img = base_background()
    draw = ImageDraw.Draw(img, 'RGBA')

    # Eyebrow
    eyebrow_font = font(20, "bold")
    draw_pill(draw, (60, 60), "  DATA · IA · MICROSOFT FABRIC  ", eyebrow_font,
              bg=(15, 25, 45, 220), fg=CYAN_300, pad=(4, 6))

    # Main title (H1)
    title_font_big = font(90, "black")
    title_font_med = font(64, "black")

    # Line 1: "Fran Fuerte"
    draw.text((60, 130), "Fran Fuerte", fill=WHITE, font=title_font_big)

    # Line 2: gradient effect with two colors — subtitle
    # Use two lines
    draw.text((60, 240), "Data Architect & AI Engineer", fill=VIOLET_300, font=title_font_med)
    draw.text((60, 315), "en Microsoft Fabric", fill=CYAN_300, font=title_font_med)

    # Bottom description line
    desc_font = font(24, "regular")
    draw.text((60, 425),
              "Data Analytics Manager en Avanade · Microsoft Fabric Champion 2025",
              fill=SLATE_300, font=desc_font)
    draw.text((60, 460),
              "Power BI Champion 2024 · Blog técnico en español",
              fill=SLATE_400, font=desc_font)

    # Certifications row
    cert_row_y = 520
    x_cursor = 60
    certs = [
        ("DP-700", CYAN_400),
        ("DP-600", VIOLET_500),
        ("DP-500", (99, 102, 241)),
        ("DP-203", (59, 130, 246)),
        ("PL-300", (251, 191, 36)),
    ]
    overlays = []
    for code, color in certs:
        overlay, code_txt, f_obj, txt_xy, accent = draw_cert_chip(draw, (x_cursor, cert_row_y), code, color)
        overlays.append((overlay, code_txt, f_obj, txt_xy, accent))
        tw = ImageDraw.Draw(overlay).textlength(code, font=f_obj)
        x_cursor += int(tw + 46)

    img_rgba = img.convert('RGBA')
    for overlay, code, f_obj, txt_xy, accent in overlays:
        img_rgba = Image.alpha_composite(img_rgba, overlay)
    img = img_rgba.convert('RGB')
    draw = ImageDraw.Draw(img, 'RGBA')
    for overlay, code, f_obj, txt_xy, accent in overlays:
        # redraw the text on top
        draw.text(txt_xy, code, fill=accent, font=f_obj)

    # URL bottom-right
    url_font = font(20, "bold")
    url = "www.franfuerte.com"
    tw = draw.textlength(url, font=url_font)
    draw.text((W - tw - 60, H - 55), url, fill=CYAN_300, font=url_font)

    # Subtle border for polish
    draw.rectangle((0, 0, W-1, H-1), outline=(*VIOLET_500, 40), width=2)

    path = os.path.join(OUT, 'og-default.png')
    img.save(path, 'PNG', optimize=True)
    print(f"OK og-default.png ({os.path.getsize(path)//1024} KB)")


# ── Contacto page OG ─────────────────────────────────────────────────────────

def gen_contacto():
    img = base_background()
    draw = ImageDraw.Draw(img, 'RGBA')

    draw_pill(draw, (60, 60), "  ASESORÍA · GOVERNANCE · AUDITORÍAS  ",
              font(20, "bold"), bg=(15, 25, 45, 220), fg=CYAN_300, pad=(4, 6))

    title_font = font(78, "black")
    draw.text((60, 140), "¿Atascado con Fabric", fill=WHITE, font=title_font)
    draw.text((60, 230), "o Power BI?", fill=WHITE, font=title_font)
    draw.text((60, 335), "Vamos a desatascarlo.", fill=CYAN_300, font=title_font)

    desc_font = font(24, "regular")
    draw.text((60, 460), "Asesoría · Mentorías · Governance · Auditorías", fill=SLATE_300, font=desc_font)
    draw.text((60, 495), "Fran Fuerte · Microsoft Fabric Champion 2025", fill=SLATE_400, font=desc_font)

    url_font = font(20, "bold")
    url = "www.franfuerte.com/contacto"
    tw = draw.textlength(url, font=url_font)
    draw.text((W - tw - 60, H - 55), url, fill=CYAN_300, font=url_font)

    draw.rectangle((0, 0, W-1, H-1), outline=(*VIOLET_500, 40), width=2)

    path = os.path.join(OUT, 'og-contacto.png')
    img.save(path, 'PNG', optimize=True)
    print(f"OK og-contacto.png ({os.path.getsize(path)//1024} KB)")


# ── Blog OG (generic) ─────────────────────────────────────────────────────────

def gen_blog():
    img = base_background()
    draw = ImageDraw.Draw(img, 'RGBA')

    draw_pill(draw, (60, 60), "  BLOG TÉCNICO EN ESPAÑOL  ",
              font(20, "bold"), bg=(15, 25, 45, 220), fg=CYAN_300, pad=(4, 6))

    title_font = font(84, "black")
    draw.text((60, 140), "Blog", fill=WHITE, font=font(120, "black"))

    subtitle_font = font(48, "bold")
    draw.text((60, 290), "Microsoft Fabric · Power BI", fill=VIOLET_300, font=subtitle_font)
    draw.text((60, 350), "Arquitectura de datos · IA", fill=CYAN_300, font=subtitle_font)

    desc_font = font(24, "regular")
    draw.text((60, 460), "Artículos técnicos con criterio real. Sin humo. Sin relleno.", fill=SLATE_300, font=desc_font)
    draw.text((60, 495), "Fran Fuerte · Data Analytics Manager en Avanade", fill=SLATE_400, font=desc_font)

    url_font = font(20, "bold")
    url = "www.franfuerte.com/blog"
    tw = draw.textlength(url, font=url_font)
    draw.text((W - tw - 60, H - 55), url, fill=CYAN_300, font=url_font)

    draw.rectangle((0, 0, W-1, H-1), outline=(*VIOLET_500, 40), width=2)

    path = os.path.join(OUT, 'og-blog.png')
    img.save(path, 'PNG', optimize=True)
    print(f"OK og-blog.png ({os.path.getsize(path)//1024} KB)")


gen_default()
gen_contacto()
gen_blog()
print("\nAll OG images generated in public/og/")
