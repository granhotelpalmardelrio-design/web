from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


SOURCE = Path(r"C:\Users\jabra\.codex\generated_images\01a05857-f493-73c3-a8eb-0bf146a7c195\exec-a39c1092-7ebc-4041-bbb6-7f432b4c213e.png")
OUT = Path(r"C:\Users\jabra\Downloads\Palmar del Río\desayuno-elementos-transparentes")
SCALE = 4


def antialiased_mask(size, shapes, feather=0.45):
    """Draw precise masks at 4x resolution and reduce for clean transparent edges."""
    large = Image.new("L", (size[0] * SCALE, size[1] * SCALE), 0)
    draw = ImageDraw.Draw(large)

    def scaled(values):
        return tuple(round(v * SCALE) for v in values)

    for shape, points in shapes:
        if shape == "ellipse":
            draw.ellipse(scaled(points), fill=255)
        elif shape == "polygon":
            draw.polygon([scaled(point) for point in points], fill=255)
        else:
            raise ValueError(shape)

    if feather:
        large = large.filter(ImageFilter.GaussianBlur(feather * SCALE))
    return large.resize(size, Image.Resampling.LANCZOS)


def save_cutout(source, mask, filename):
    cutout = source.copy()
    cutout.putalpha(mask)
    cutout.save(OUT / filename, optimize=True)


def checkerboard(size, tile=22):
    board = Image.new("RGB", size, "#EFEFEF")
    draw = ImageDraw.Draw(board)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            if (x // tile + y // tile) % 2:
                draw.rectangle((x, y, x + tile - 1, y + tile - 1), fill="#D8D8D8")
    return board


def make_preview(paths, destination):
    panels = []
    for path in paths:
        transparent = Image.open(path).convert("RGBA")
        panel = checkerboard(transparent.size)
        panel.paste(transparent, (0, 0), transparent)
        panel.thumbnail((235, 418), Image.Resampling.LANCZOS)
        panels.append(panel)
    sheet = Image.new("RGB", (235 * 4, 418 * 2), "#F4EEE7")
    for i, panel in enumerate(panels):
        sheet.paste(panel, ((i % 4) * 235, (i // 4) * 418))
    sheet.save(destination, quality=94)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source = Image.open(SOURCE).convert("RGBA")
    size = source.size

    masks = {
        # Complete serving pieces are retained for coffee, fruit, jam and juice.
        "frutas": antialiased_mask(size, [("ellipse", (405, 452, 627, 682))], 0.55),
        "pan": antialiased_mask(size, [("polygon", [
            (116, 914), (122, 873), (145, 850), (178, 841), (226, 844),
            (261, 855), (286, 884), (298, 925), (304, 974), (303, 1028),
            (293, 1078), (271, 1120), (243, 1141), (204, 1148), (167, 1138),
            (137, 1114), (120, 1073), (112, 1028), (113, 968)
        ])], 0.65),
        "huevo": antialiased_mask(size, [("polygon", [
            (274, 1010), (293, 982), (327, 968), (370, 964), (418, 971),
            (454, 988), (477, 1015), (483, 1047), (500, 1071), (513, 1104),
            (510, 1146), (486, 1180), (450, 1202), (404, 1213), (357, 1208),
            (314, 1191), (282, 1160), (267, 1124), (266, 1068)
        ])], 0.65),
        "tortilla": antialiased_mask(size, [("polygon", [
            (493, 852), (522, 839), (551, 848), (574, 875), (587, 918),
            (594, 969), (590, 1021), (576, 1061), (553, 1084), (522, 1091),
            (495, 1078), (477, 1050), (469, 1008), (468, 957), (474, 904)
        ])], 0.65),
        "mermelada": antialiased_mask(size, [("ellipse", (296, 798, 459, 963))], 0.55),
        "cafe": antialiased_mask(size, [("ellipse", (47, 427, 378, 747))], 0.65),
        "jugo": antialiased_mask(size, [
            ("polygon", [(671, 488), (678, 565), (685, 637), (699, 671),
                         (722, 686), (808, 686), (832, 672), (845, 640),
                         (851, 566), (855, 488)]),
            ("ellipse", (671, 462, 855, 523)),
            ("ellipse", (698, 652, 831, 691)),
        ], 0.55),
    }

    filenames = {
        "frutas": "01-frutas-transparente.png",
        "pan": "02-pan-transparente.png",
        "huevo": "03-huevo-transparente.png",
        "tortilla": "04-tortilla-verde-transparente.png",
        "mermelada": "05-mermelada-transparente.png",
        "cafe": "06-cafe-transparente.png",
        "jugo": "07-jugo-transparente.png",
    }

    paths = []
    for name, filename in filenames.items():
        save_cutout(source, masks[name], filename)
        paths.append(OUT / filename)
    make_preview(paths, OUT / "preview-elementos-transparentes.jpg")

    for path in paths:
        image = Image.open(path)
        alpha = image.getchannel("A")
        print(f"{path.name}: {image.size}, alpha bbox={alpha.getbbox()}")


if __name__ == "__main__":
    main()
