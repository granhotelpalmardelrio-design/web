from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image


SOURCE = Path(
    r"C:\Users\jabra\.codex\generated_images\01a05857-f493-73c3-a8eb-0bf146a7c195"
    r"\exec-61dbbd85-6c0c-481c-9b31-bbc4fffea89e.png"
)
OUTPUT = Path(r"C:\Users\jabra\Downloads\Palmar del Río\desayuno-guia-incognitas-latte.png")

image = Image.open(SOURCE).convert("RGB")
pixels = np.asarray(image).copy()
height, width, _ = pixels.shape

# The generated stroke is approximately #D2A26C. Restrict detection to the
# upper mystery row so the four coffee-colored outlines on the plate stay intact.
reference = np.array([210.0, 162.0, 108.0])
target = np.array([246.0, 245.0, 243.0])  # Exact requested latte: #F6F5F3
rgb = pixels.astype(np.float32)
distance = np.linalg.norm(rgb - reference, axis=2)

r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
orange_family = (
    (r > 150)
    & (r - g > 18)
    & (r - g < 95)
    & (g - b > 15)
    & (g - b < 105)
)
upper_band = np.zeros((height, width), dtype=bool)
upper_band[390:750, :] = True

# Limit the color search to narrow geometric bands around the three known
# outlines. This prevents similarly colored terrazzo chips from entering the
# mask even when they happen to touch one another.
yy, xx = np.mgrid[0:height, 0:width]
coffee_radius = np.sqrt(((xx - 215) / 154) ** 2 + ((yy - 580) / 151) ** 2)
fruit_radius = np.sqrt(((xx - 512) / 107) ** 2 + ((yy - 568) / 108) ** 2)
juice_radius = np.sqrt(((xx - 774) / 101) ** 2 + ((yy - 574) / 100) ** 2)
coffee_band = ((coffee_radius > 0.82) & (coffee_radius < 1.18)) | (
    (xx >= 38) & (xx <= 92) & (yy >= 525) & (yy <= 635)
)
fruit_band = (fruit_radius > 0.78) & (fruit_radius < 1.22)
juice_band = (juice_radius > 0.78) & (juice_radius < 1.22)
geometry = coffee_band | fruit_band | juice_band

core = (distance < 48) & orange_family & upper_band & geometry

# Retain only substantial connected regions. Granite flecks with similar colors
# are small and disappear, while every thick dash remains.
visited = np.zeros_like(core)
stroke_core = np.zeros_like(core)
component_sizes = []
for y in range(390, min(750, height)):
    for x in range(width):
        if not core[y, x] or visited[y, x]:
            continue
        queue = deque([(y, x)])
        visited[y, x] = True
        component = []
        while queue:
            cy, cx = queue.popleft()
            component.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    ny, nx = cy + dy, cx + dx
                    if (
                        390 <= ny < min(750, height)
                        and 0 <= nx < width
                        and core[ny, nx]
                        and not visited[ny, nx]
                    ):
                        visited[ny, nx] = True
                        queue.append((ny, nx))
        if len(component) >= 55:
            component_sizes.append(len(component))
            for cy, cx in component:
                stroke_core[cy, cx] = True

# Grow two pixels into antialiased orange edge pixels, without touching unrelated
# granite. This keeps the rounded dashes smooth.
stroke = stroke_core.copy()
relaxed = (distance < 100) & orange_family & upper_band & geometry
for _ in range(2):
    grown = stroke.copy()
    grown[1:, :] |= stroke[:-1, :]
    grown[:-1, :] |= stroke[1:, :]
    grown[:, 1:] |= stroke[:, :-1]
    grown[:, :-1] |= stroke[:, 1:]
    stroke |= grown & relaxed

# Replace solid interiors exactly and softly blend only the antialiased boundary.
weight = np.clip((100.0 - distance) / 45.0, 0.0, 1.0)
weight[distance <= 55] = 1.0
weight *= stroke
pixels = np.rint(rgb * (1.0 - weight[:, :, None]) + target * weight[:, :, None]).clip(0, 255).astype(np.uint8)

Image.fromarray(pixels, "RGB").save(OUTPUT, quality=100)
print(f"Saved: {OUTPUT}")
print(f"Recolored pixels: {int(stroke.sum())}")
print(f"Retained dash components: {len(component_sizes)}")
