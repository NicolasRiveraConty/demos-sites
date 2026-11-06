#!/usr/bin/env python3
"""Gera a wordmark da Conty e os GIFs de simulação do tutorial de criadores.

As imagens são mockups desenhados à mão (Pillow). Não são capturas do produto.
Rode a partir de qualquer pasta:

    python3 help-tutoriais/scripts/gerar-gifs-mock.py
"""

from __future__ import annotations

import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GIF_DIR = os.path.join(ROOT, "images", "tutoriais", "buscar-criadores")
LOGO_DIR = os.path.join(ROOT, "logo")

INTER = {
    "regular": "/usr/share/fonts/truetype/macos/Inter-Regular.ttf",
    "medium": "/usr/share/fonts/truetype/macos/Inter-Medium.ttf",
    "semibold": "/usr/share/fonts/truetype/macos/Inter-SemiBold.ttf",
    "bold": "/usr/share/fonts/truetype/macos/Inter-Bold.ttf",
}

W, H = 960, 640
SIDEBAR_W = 300
BLUE = "#1A73E8"
BLUE_DARK = "#185ABC"
BLUE_SOFT = "#E8F0FE"
INK = "#1F2937"
MUTED = "#6B7280"
LINE = "#E5E7EB"
SIDEBAR_BG = "#EEF1F6"
CANVAS = "#F7F8FB"
WHITE = "#FFFFFF"
AMBER_BG = "#FEF3C7"
AMBER_INK = "#92400E"
AMBER_LINE = "#F59E0B"
GREEN = "#1E8E3E"


def font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(INTER[weight], size)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def rounded(draw: ImageDraw.ImageDraw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def alpha_ellipse(base: Image.Image, box, fill) -> Image.Image:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).ellipse(box, fill=fill)
    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def measure(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont):
    box = draw.textbbox((0, 0), text, font=face)
    return box[2] - box[0], box[3] - box[1]


def icon(draw, kind: str, x: int, y: int, color: str):
    if kind == "house":
        draw.line([(x + 1, y + 8), (x + 9, y + 1), (x + 17, y + 8)], fill=color, width=2)
        draw.rounded_rectangle([x + 3, y + 8, x + 15, y + 17], radius=1, outline=color, width=2)
    elif kind == "megaphone":
        draw.polygon(
            [(x + 1, y + 6), (x + 7, y + 6), (x + 15, y + 2), (x + 15, y + 14), (x + 7, y + 11), (x + 1, y + 11)],
            outline=color,
        )
        draw.line([(x + 6, y + 12), (x + 5, y + 16)], fill=color, width=2)
    elif kind == "search":
        draw.ellipse([x + 1, y + 1, x + 12, y + 12], outline=color, width=2)
        draw.line([(x + 11, y + 11), (x + 16, y + 16)], fill=color, width=2)
    elif kind == "message":
        rounded(draw, [x + 1, y + 2, x + 16, y + 13], 3, outline=color, width=2)
        draw.polygon([(x + 4, y + 12), (x + 4, y + 17), (x + 9, y + 12)], fill=color)
    elif kind == "users":
        draw.ellipse([x + 1, y + 1, x + 8, y + 8], outline=color, width=2)
        draw.ellipse([x + 9, y + 2, x + 16, y + 9], outline=color, width=2)
        draw.arc([x - 1, y + 9, x + 10, y + 18], 200, 340, fill=color, width=2)
        draw.arc([x + 7, y + 10, x + 18, y + 19], 200, 340, fill=color, width=2)
    elif kind == "wallet":
        rounded(draw, [x + 1, y + 4, x + 17, y + 16], 2, outline=color, width=2)
        draw.ellipse([x + 11, y + 8, x + 15, y + 12], outline=color, width=2)
    elif kind == "card":
        rounded(draw, [x + 1, y + 3, x + 17, y + 15], 2, outline=color, width=2)
        draw.line([(x + 1, y + 7), (x + 17, y + 7)], fill=color, width=2)
    elif kind == "transfer":
        draw.line([(x + 2, y + 5), (x + 14, y + 5)], fill=color, width=2)
        draw.line([(x + 4, y + 12), (x + 16, y + 12)], fill=color, width=2)
        draw.polygon([(x + 12, y + 2), (x + 17, y + 5), (x + 12, y + 8)], fill=color)
        draw.polygon([(x + 6, y + 9), (x + 1, y + 12), (x + 6, y + 15)], fill=color)
    elif kind == "bag":
        draw.arc([x + 5, y + 1, x + 13, y + 8], 200, 340, fill=color, width=2)
        rounded(draw, [x + 2, y + 6, x + 16, y + 17], 3, outline=color, width=2)


def nav_layout():
    """Caixas do menu, espelhando a ordem do print do painel da marca."""
    items = [
        ("dashboard", "Dashboard", "house", False),
        ("campanhas", "Campanhas", "megaphone", False),
        ("criadores", "Criadores", "search", False),
        ("mensagens", "Mensagens", "message", False),
        ("comunidades", "Comunidades", "users", False),
        ("financeiro", "Financeiro", "bag", False),
        ("pagamentos", "Pagamentos", "wallet", True),
        ("assinatura", "Assinatura", "card", True),
        ("repasses", "Repasses", "transfer", True),
    ]
    y = 136
    boxes = {}
    for item_id, label, kind, sub in items:
        height = 34 if sub else 40
        x = 28 if sub else 14
        width = SIDEBAR_W - x - 14
        boxes[item_id] = {
            "label": label,
            "kind": kind,
            "sub": sub,
            "box": (x, y, width, height),
        }
        y += height + 4
    return boxes


def draw_cursor(draw: ImageDraw.ImageDraw, x: int, y: int):
    pts = [(x, y), (x, y + 20), (x + 5, y + 15), (x + 9, y + 23), (x + 12, y + 21), (x + 9, y + 13), (x + 16, y + 13)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            draw.polygon([(px + dx, py + dy) for px, py in pts], fill=WHITE)
    draw.polygon(pts, fill="#111827")


def draw_badge(draw: ImageDraw.ImageDraw):
    face = font(12, "bold")
    text = "SIMULAÇÃO"
    tw, th = measure(draw, text, face)
    pad_x, pad_y = 10, 5
    width, height = tw + pad_x * 2, th + pad_y * 2
    x, y = W - width - 18, 16
    rounded(draw, [x, y, x + width, y + height], height / 2, fill=AMBER_BG, outline=AMBER_LINE, width=1)
    draw.text((x + pad_x, y + height / 2), text, font=face, fill=AMBER_INK, anchor="lm")


def draw_sidebar(draw: ImageDraw.ImageDraw, active: str):
    draw.rectangle([0, 0, SIDEBAR_W, H], fill=SIDEBAR_BG)
    draw.line([(SIDEBAR_W, 0), (SIDEBAR_W, H)], fill="#E2E6EE", width=1)
    draw.text((22, 28), "conty", font=font(26, "bold"), fill=BLUE, anchor="lm")

    rounded(draw, [16, 58, SIDEBAR_W - 16, 116], 14, fill=WHITE)
    rounded(draw, [28, 72, 64, 104], 10, fill="#5C3D6E")
    draw.text((40, 88), "Aa", font=font(14, "bold"), fill=WHITE, anchor="mm")
    draw.text((76, 78), "MARCA", font=font(10, "semibold"), fill="#9CA3AF", anchor="lt")
    draw.text((76, 94), "Marca Alfa", font=font(14, "bold"), fill=INK, anchor="lt")
    for row in range(3):
        for col in range(4):
            cx = 214 + col * 8
            cy = 74 + row * 8
            draw.ellipse([cx, cy, cx + 2, cy + 2], fill="#D1D5DB")
    draw.ellipse([248, 78, 264, 94], outline=BLUE, width=2)

    boxes = nav_layout()
    for item_id, meta in boxes.items():
        x, y, width, height = meta["box"]
        selected = item_id == active
        if selected:
            rounded(draw, [x, y, x + width, y + height], 10, fill=BLUE_SOFT)
        color = BLUE if selected else INK
        weight = "semibold" if selected else "medium"
        ix = x + (18 if meta["sub"] else 14)
        iy = y + height / 2
        icon(draw, meta["kind"], ix, int(iy - 9), BLUE)
        label_x = ix + 26
        draw.text((label_x, iy), meta["label"], font=font(15, weight), fill=color, anchor="lm")
        if item_id == "mensagens":
            draw.ellipse([ix + 8, iy - 14, ix + 22, iy], fill=BLUE)
            draw.text((ix + 15, iy - 7), "3", font=font(9, "bold"), fill=WHITE, anchor="mm")
        if item_id == "financeiro":
            draw.line([(x + width - 22, iy - 3), (x + width - 16, iy + 3), (x + width - 10, iy - 3)], fill=MUTED, width=2)

    card_top = 548
    rounded(draw, [16, card_top, SIDEBAR_W - 16, H - 16], 14, fill=WHITE)
    draw.text((28, card_top + 16), "Total", font=font(11, "medium"), fill=MUTED, anchor="lt")
    draw.text((28, card_top + 36), "R$ •••", font=font(18, "bold"), fill=INK, anchor="lt")
    draw.text((118, card_top + 40), "fictício", font=font(11, "medium"), fill=AMBER_INK, anchor="lt")
    draw.rounded_rectangle([28, card_top + 62, SIDEBAR_W - 32, card_top + 68], radius=3, fill="#E5E7EB")
    draw.rounded_rectangle([28, card_top + 62, 120, card_top + 68], radius=3, fill=GREEN)


def target_point(item_id: str):
    x, y, width, height = nav_layout()[item_id]["box"]
    # Mira no rótulo do item, não na borda direita da linha.
    return x + 86, y + height / 2, (x, y, width, height)


def outline_box(base: Image.Image, box, pad: int = 3, alpha: int = 230) -> Image.Image:
    x, y, width, height = box
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rounded_rectangle(
        [x - pad, y - pad, x + width + pad, y + height + pad],
        radius=12,
        outline=(*bytes.fromhex(BLUE[1:]), alpha),
        width=4,
    )
    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def ring(base: Image.Image, cx: float, cy: float, radius: float, alpha: int = 180) -> Image.Image:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=(*bytes.fromhex(BLUE[1:]), alpha), width=4)
    inner = max(8, radius - 10)
    draw.ellipse(
        [cx - inner, cy - inner, cx + inner, cy + inner],
        outline=(*bytes.fromhex("8AB4F8"), max(40, alpha - 40)),
        width=3,
    )
    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def chip(draw: ImageDraw.ImageDraw, text: str, x: int, y: int):
    face = font(13, "bold")
    tw, th = measure(draw, text, face)
    width, height = tw + 22, th + 12
    rounded(draw, [x, y, x + width, y + height], 8, fill=BLUE)
    draw.text((x + 11, y + height / 2), text, font=face, fill=WHITE, anchor="lm")
    return width, height


def new_frame(active: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (W, H), CANVAS)
    draw = ImageDraw.Draw(image)
    draw_sidebar(draw, active)
    return image, draw


def content_title(draw, title: str):
    draw.text((SIDEBAR_W + 28, 78), title, font=font(22, "bold"), fill=INK, anchor="lm")


def search_box(draw, text: str, focused: bool):
    draw.text((SIDEBAR_W + 28, 102), "Campo ilustrativo", font=font(11, "semibold"), fill=AMBER_INK, anchor="lt")
    box = [SIDEBAR_W + 28, 120, 748, 168]
    outline = BLUE if focused else "#D1D5DB"
    width = 2 if focused else 1
    rounded(draw, box, 12, fill=WHITE, outline=outline, width=width)
    if text:
        draw.text((box[0] + 16, 144), text, font=font(16, "medium"), fill=INK, anchor="lm")
        caret_x = box[0] + 20 + measure(draw, text, font(16, "medium"))[0]
        draw.line([(caret_x, 132), (caret_x, 156)], fill=BLUE, width=2)
    else:
        draw.text((box[0] + 16, 144), "nome do criador", font=font(16, "regular"), fill="#9CA3AF", anchor="lm")
    return box


def filter_button(draw, hot: bool):
    box = [764, 120, W - 28, 168]
    fill = BLUE_SOFT if hot else WHITE
    outline = BLUE if hot else "#D1D5DB"
    rounded(draw, box, 12, fill=fill, outline=outline, width=2 if hot else 1)
    draw.text(((box[0] + box[2]) / 2, 144), "Filtros", font=font(15, "semibold"), fill=BLUE, anchor="mm")
    return box


def creator_row(draw, y: int, name: str, hot: bool, right: int | None = None):
    box = [SIDEBAR_W + 28, y, right or (W - 28), y + 64]
    if hot:
        rounded(draw, box, 12, fill=BLUE_SOFT, outline=BLUE, width=2)
    else:
        rounded(draw, box, 12, fill=WHITE, outline=LINE, width=1)
    draw.ellipse([box[0] + 16, y + 16, box[0] + 48, y + 48], fill="#DBE7FB")
    draw.text((box[0] + 32, y + 32), name[:1], font=font(16, "bold"), fill=BLUE, anchor="mm")
    draw.text((box[0] + 64, y + 24), name, font=font(15, "semibold"), fill=INK, anchor="lt")
    draw.text((box[0] + 64, y + 44), "criador ilustrativo", font=font(12, "regular"), fill=MUTED, anchor="lt")
    return box


def filter_panel(draw):
    box = [764, 176, W - 28, 320]
    rounded(draw, box, 12, fill=WHITE, outline=BLUE, width=2)
    draw.text((box[0] + 14, box[1] + 18), "Filtros", font=font(13, "bold"), fill=INK, anchor="lt")
    draw.text((box[0] + 14, box[1] + 38), "opções ilustrativas", font=font(11, "medium"), fill=AMBER_INK, anchor="lt")
    for index in range(3):
        top = box[1] + 62 + index * 28
        rounded(draw, [box[0] + 14, top, box[2] - 14, top + 18], 6, fill="#F3F4F6")
    return box


def profile_card(draw, progress: float):
    full_h = 168
    height = int(full_h * progress)
    if height < 8:
        return None
    top = 430
    box = [SIDEBAR_W + 28, top, W - 28, top + height]
    rounded(draw, box, 12, fill=WHITE, outline=BLUE, width=2)
    if height < 36:
        return box
    draw.text((box[0] + 18, box[1] + 16), "Perfil ilustrativo", font=font(12, "bold"), fill=AMBER_INK, anchor="lt")
    if height < 70:
        return box
    draw.text((box[0] + 18, box[1] + 40), "Marina Alves", font=font(18, "bold"), fill=INK, anchor="lt")
    if height < 110:
        return box
    draw.text((box[0] + 18, box[1] + 68), "informações ilustrativas", font=font(12, "medium"), fill=MUTED, anchor="lt")
    for index in range(3):
        y = box[1] + 92 + index * 22
        if y + 12 > box[3] - 8:
            break
        rounded(draw, [box[0] + 18, y, box[2] - 18, y + 12], 4, fill="#F3F4F6")
    return box


def finish(image: Image.Image, cursor=None, pulse=None, box=None) -> Image.Image:
    if box:
        image = outline_box(image, box)
    if pulse:
        cx, cy, radius, alpha = pulse
        image = ring(image, cx, cy, radius, alpha)
    draw = ImageDraw.Draw(image)
    if cursor:
        draw_cursor(draw, int(cursor[0]), int(cursor[1]))
    draw_badge(draw)
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, H - 1], radius=18, fill=255)
    background = Image.new("RGB", image.size, WHITE)
    background.paste(image, (0, 0), mask)
    return background


def scene_sidebar(active: str, cursor=None, pulse=None, callout=None, callout_y: int = 430, highlight=None) -> Image.Image:
    image, draw = new_frame(active)
    content_title(draw, "Painel da marca")
    draw.text(
        (SIDEBAR_W + 28, 118),
        "O menu à esquerda é uma simulação do painel.",
        font=font(14, "regular"),
        fill=MUTED,
        anchor="lt",
    )
    if callout:
        chip(draw, callout, SIDEBAR_W + 36, callout_y)
    return finish(image, cursor, pulse, box=highlight)


def scene_search(query: str, focused: str, show_panel: bool, cursor=None, pulse=None, callout=None) -> Image.Image:
    image, draw = new_frame("criadores")
    content_title(draw, "Criadores")
    search_box(draw, query, focused == "search")
    filter_button(draw, focused == "filters" or show_panel)
    names = ["Marina Alves", "João Pires", "Lia Nunes"]
    right = 748 if show_panel else None
    for index, name in enumerate(names):
        # Destaca quem começa com o texto digitado e mantém as outras linhas visíveis.
        hot = bool(query) and name.lower().startswith(query.lower())
        creator_row(draw, 186 + index * 76, name, hot and not show_panel, right=right)
    if show_panel:
        filter_panel(draw)
    if callout:
        chip(draw, callout, SIDEBAR_W + 28, 186 + 3 * 76)
    return finish(image, cursor, pulse)


def scene_profile(hot: bool, progress: float, cursor=None, pulse=None, callout=None) -> Image.Image:
    image, draw = new_frame("criadores")
    content_title(draw, "Criadores")
    names = ["Marina Alves", "João Pires", "Lia Nunes"]
    for index, name in enumerate(names):
        creator_row(draw, 108 + index * 76, name, hot and index == 0)
    if progress > 0:
        profile_card(draw, progress)
    if callout and progress < 0.4:
        chip(draw, callout, SIDEBAR_W + 210, 60)
    return finish(image, cursor, pulse)


def frames_abrir():
    cx, cy, (row_x, row_y, _row_w, _row_h) = target_point("criadores")
    callout_y = int(row_y)
    start = (720, 300)
    frames = []
    durations = []
    # Repouso no Dashboard.
    frames.append(scene_sidebar("dashboard"))
    durations.append(500)
    for step in range(1, 6):
        t = ease(step / 5)
        cursor = (lerp(start[0], cx, t), lerp(start[1], cy, t))
        frames.append(scene_sidebar("dashboard", cursor=cursor))
        durations.append(90)
    row_box = (row_x, row_y, _row_w, _row_h)
    frames.append(
        scene_sidebar(
            "dashboard",
            cursor=(cx + 70, cy),
            highlight=row_box,
            callout="Clique em Criadores",
            callout_y=callout_y,
        )
    )
    durations.append(280)
    frames.append(
        scene_sidebar(
            "dashboard",
            cursor=(cx + 64, cy + 2),
            highlight=row_box,
            callout="Clique em Criadores",
            callout_y=callout_y,
        )
    )
    durations.append(220)
    frames.append(scene_sidebar("criadores", cursor=(cx - 6, cy + 2), callout="Criadores aberto", callout_y=callout_y))
    durations.append(280)
    frames.append(scene_sidebar("criadores", callout="Criadores aberto", callout_y=callout_y))
    durations.append(900)
    return frames, durations


def frames_buscar():
    frames = []
    durations = []
    search_at = (SIDEBAR_W + 180, 144)
    filter_at = (860, 144)
    frames.append(scene_search("", "", False))
    durations.append(400)
    for step in range(1, 4):
        t = ease(step / 3)
        cursor = (lerp(700, search_at[0], t), lerp(320, search_at[1], t))
        frames.append(scene_search("", "", False, cursor=cursor))
        durations.append(90)
    frames.append(scene_search("", "search", False, cursor=search_at, pulse=(search_at[0], search_at[1], 22, 200), callout="Digite o nome"))
    durations.append(180)
    query = ""
    for letter in "Marina":
        query += letter
        frames.append(scene_search(query, "search", False, cursor=(search_at[0] + 70, search_at[1])))
        durations.append(150)
    frames.append(scene_search("Marina", "search", False, callout="Nome digitado"))
    durations.append(350)
    for step in range(1, 4):
        t = ease(step / 3)
        cursor = (lerp(search_at[0] + 70, filter_at[0], t), lerp(search_at[1], filter_at[1], t))
        frames.append(scene_search("Marina", "search", False, cursor=cursor))
        durations.append(90)
    frames.append(
        scene_search(
            "Marina",
            "filters",
            False,
            cursor=filter_at,
            pulse=(filter_at[0], filter_at[1], 24, 210),
            callout="Ou use os filtros",
        )
    )
    durations.append(180)
    frames.append(scene_search("Marina", "filters", True, cursor=(filter_at[0] - 4, filter_at[1] + 2)))
    durations.append(250)
    frames.append(scene_search("Marina", "filters", True))
    durations.append(900)
    return frames, durations


def frames_perfil():
    frames = []
    durations = []
    row_at = (W - 80, 140)
    frames.append(scene_profile(False, 0))
    durations.append(400)
    for step in range(1, 5):
        t = ease(step / 4)
        cursor = (lerp(700, row_at[0], t), lerp(360, row_at[1], t))
        frames.append(scene_profile(False, 0, cursor=cursor))
        durations.append(90)
    frames.append(scene_profile(False, 0, cursor=row_at, pulse=(row_at[0], row_at[1], 26, 210), callout="Abra o criador"))
    durations.append(180)
    frames.append(scene_profile(True, 0.15, cursor=(row_at[0] - 4, row_at[1] + 2)))
    durations.append(120)
    for progress in (0.4, 0.7, 1.0):
        frames.append(scene_profile(True, progress))
        durations.append(140)
    frames.append(scene_profile(True, 1))
    durations.append(1000)
    return frames, durations


def save_gif(frames, durations, filename: str):
    os.makedirs(GIF_DIR, exist_ok=True)
    path = os.path.join(GIF_DIR, filename)
    sample = frames[0].copy()
    sample.thumbnail((480, 320))
    palette = sample.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    converted = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    converted[0].save(
        path,
        save_all=True,
        append_images=converted[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"{filename}: {len(frames)} frames, {os.path.getsize(path) // 1024} KB")


def glyph_path(font_file: str, text: str, pixel_size: float, color: str):
    tt = TTFont(font_file)
    glyph_set = tt.getGlyphSet()
    cmap = tt.getBestCmap()
    ascent = tt["hhea"].ascent
    descent = tt["hhea"].descent
    scale = pixel_size / tt["head"].unitsPerEm
    pad = 1
    baseline = pad + ascent * scale
    height = pad * 2 + (ascent - descent) * scale
    x = pad
    commands = []
    for char in text:
        glyph = glyph_set[cmap[ord(char)]]
        pen = SVGPathPen(glyph_set)
        wrapper = TransformPen(pen, (scale, 0, 0, -scale, x, baseline))
        glyph.draw(wrapper)
        commands.append(pen.getCommands())
        x += glyph.width * scale
    width = x + pad
    path = " ".join(commands)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.2f}" height="{height:.2f}" '
        f'viewBox="0 0 {width:.2f} {height:.2f}" fill="none">\n'
        f'  <path d="{path}" fill="{color}"/>\n'
        f"</svg>\n"
    )
    return svg, width, height


def write_logos():
    os.makedirs(LOGO_DIR, exist_ok=True)
    light, _, _ = glyph_path(INTER["bold"], "conty", 28, BLUE)
    dark, _, _ = glyph_path(INTER["bold"], "conty", 28, "#FFFFFF")
    with open(os.path.join(LOGO_DIR, "light.svg"), "w", encoding="utf-8") as handle:
        handle.write(light)
    with open(os.path.join(LOGO_DIR, "dark.svg"), "w", encoding="utf-8") as handle:
        handle.write(dark)

    _svg, mark_w, mark_h = glyph_path(INTER["bold"], "c", 36, "#FFFFFF")
    path = _svg.split('d="', 1)[1].split('"', 1)[0]
    # O glifo minúsculo fica na base do em square. Sobe um pouco para centralizar.
    tx = (64 - mark_w) / 2
    ty = (64 - mark_h) / 2 - 6
    favicon = f"""<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" fill="none">
  <rect width="64" height="64" rx="16" fill="{BLUE}"/>
  <path transform="translate({tx:.2f} {ty:.2f})" d="{path}" fill="#FFFFFF"/>
</svg>
"""
    with open(os.path.join(ROOT, "favicon.svg"), "w", encoding="utf-8") as handle:
        handle.write(favicon)
    print("logos escritos")


def main():
    write_logos()
    save_gif(*frames_abrir(), "01-abrir-criadores.gif")
    save_gif(*frames_buscar(), "02-buscar-e-filtrar.gif")
    save_gif(*frames_perfil(), "03-abrir-perfil.gif")
    # Quadros de revisão, fora do site.
    preview = "/tmp/gif-preview"
    os.makedirs(preview, exist_ok=True)
    for name, builder in (
        ("01", frames_abrir),
        ("02", frames_buscar),
        ("03", frames_perfil),
    ):
        frames, _ = builder()
        for label, frame in (("a", frames[0]), ("b", frames[len(frames) // 2]), ("c", frames[-1])):
            frame.save(os.path.join(preview, f"{name}-{label}.png"))
    print("previews em", preview)


if __name__ == "__main__":
    main()
