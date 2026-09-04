from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps


MASTER = Path(r"C:\Users\jabra\.codex\generated_images\01a05857-f493-73c3-a8eb-0bf146a7c195\exec-a39c1092-7ebc-4041-bbb6-7f432b4c213e.png")
GUIDE = Path(r"C:\Users\jabra\Downloads\Palmar del Río\desayuno-guia-incognitas-latte.png")
OUT = Path(r"C:\Users\jabra\Downloads\Palmar del Río\desayuno-revelaciones")


def soft_shape(size, kind, points, blur=1.6):
    """Build a subtly feathered full-resolution alpha mask."""
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    if kind == "ellipse":
        draw.ellipse(points, fill=255)
    elif kind == "polygon":
        draw.polygon(points, fill=255)
    else:
        raise ValueError(kind)
    return mask.filter(ImageFilter.GaussianBlur(blur))


def elegant_sepia(image):
    """Neutral editorial sepia: restrained warmth, preserved contrast and texture."""
    rgb = image.convert("RGB")
    gray = ImageOps.grayscale(rgb)
    sepia = ImageOps.colorize(gray, black="#302821", mid="#9B8066", white="#EEE5D8")
    # A trace of the original prevents metal, ceramics and food from looking flat.
    return Image.blend(sepia, rgb, 0.08)


def make_contact_sheet(paths, destination):
    thumbs = []
    for path in paths:
        im = Image.open(path).convert("RGB")
        im.thumbnail((235, 418), Image.Resampling.LANCZOS)
        thumbs.append(im)
    canvas = Image.new("RGB", (235 * 4, 418 * 2), "#eee8df")
    for index, thumb in enumerate(thumbs):
        x = (index % 4) * 235
        y = (index // 4) * 418
        canvas.paste(thumb, (x, y))
    canvas.save(destination, quality=94)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    master = Image.open(MASTER).convert("RGB")
    guide = Image.open(GUIDE).convert("RGB")
    if master.size != guide.size:
        raise RuntimeError(f"Master {master.size} and guide {guide.size} do not match")

    w, h = master.size
    # The masks deliberately extend a few pixels beyond each dashed guide so the
    # revealed item completely replaces its question-mark silhouette.
    masks = {
        "frutas": soft_shape((w, h), "ellipse", (402, 448, 629, 687), 1.8),
        "pan": soft_shape(
            (w, h), "polygon",
            [(105, 885), (127, 844), (184, 828), (252, 838), (292, 874),
             (310, 949), (314, 1057), (290, 1116), (245, 1152), (175, 1148),
             (127, 1111), (109, 1040)], 1.8),
        "huevo": soft_shape(
            (w, h), "polygon",
            [(286, 958), (349, 950), (430, 960), (492, 998), (522, 1070),
             (520, 1163), (470, 1209), (393, 1232), (319, 1215), (260, 1172),
             (250, 1095), (261, 1014)], 1.8),
        "tortilla": soft_shape((w, h), "ellipse", (455, 824, 608, 1105), 1.8),
        "mermelada": soft_shape((w, h), "ellipse", (291, 794, 462, 969), 1.8),
        "cafe": soft_shape((w, h), "ellipse", (43, 422, 382, 750), 2.0),
        "jugo": soft_shape((w, h), "ellipse", (658, 448, 875, 711), 2.0),
    }

    order = ["frutas", "pan", "huevo", "tortilla", "mermelada", "cafe", "jugo"]
    filenames = [
        "01-revela-frutas.png",
        "02-revela-pan.png",
        "03-revela-huevo.png",
        "04-revela-tortilla-verde.png",
        "05-revela-mermelada.png",
        "06-revela-cafe.png",
        "07-revela-jugo.png",
    ]

    sepia_master = elegant_sepia(master)
    outputs = []
    for active_index, filename in enumerate(filenames):
        frame = guide.copy()
        # Already-guessed ingredients recede in one consistent elegant sepia.
        for name in order[:active_index]:
            frame.paste(sepia_master, (0, 0), masks[name])
        # The ingredient currently being guessed is the sole full-color focus.
        active = order[active_index]
        frame.paste(master, (0, 0), masks[active])
        # Re-seat future mystery zones over any natural food overlap (especially
        # where the bread touches the eggs) so no later answer is previewed.
        for name in order[active_index + 1:]:
            frame.paste(guide, (0, 0), masks[name])
        destination = OUT / filename
        frame.save(destination, optimize=True)
        outputs.append(destination)

    make_contact_sheet(outputs, OUT / "preview-revelaciones.jpg")
    print("\n".join(str(path) for path in outputs))


if __name__ == "__main__":
    main()
