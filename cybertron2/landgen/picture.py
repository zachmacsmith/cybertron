"""A picture of a generated land, for looking at a world while it is designed (not used by the engine): terrain colours, shaded
by relief, rivers and lakes in blue, and, once settled, the parcels, sites and roads."""
from __future__ import annotations

import numpy as np

COLOURS = {"river floodplain": (150, 190, 110), "river terrace": (190, 200, 120), "clay vale": (140, 160, 90),
           "lowland loam": (110, 150, 80), "sandy heath": (190, 170, 120), "chalk down": (200, 210, 160), "woodland": (60, 110, 60),
           "deep forest": (30, 80, 40), "hills": (150, 140, 110), "upland pasture": (170, 170, 130), "moor": (120, 100, 110),
           "fen": (110, 140, 130), "coast": (210, 200, 160), "saltmarsh": (150, 170, 150), "rock": (130, 125, 120), "water": (60, 110, 170)}
COVER_TINT = {"field": (230, 210, 120), "built": (200, 80, 60), "meadow": (170, 210, 120), "pasture": (160, 190, 100),
              "forest": (40, 100, 50)}


def render(L, path: str, world=None, scale: int = 2) -> None:
    from PIL import Image
    from cybertron2.landgen.physical import TERRAIN_NAMES
    ny, nx = L.g.shape
    img = np.zeros((ny, nx, 3))
    for i, nm in enumerate(TERRAIN_NAMES):
        img[L.terrain == i] = COLOURS.get(nm, (255, 0, 255))
    gy, gx = np.gradient(L.h)
    shade = np.clip(1 + (gx - gy) * 0.08, 0.7, 1.3)
    img *= shade[..., None]
    img[(L.river >= 1) & ~L.sea] = (70, 120, 200)
    if world is not None:
        for (r, c), cov in world.get("cover_of", {}).items():
            if cov in COVER_TINT:
                img[r, c] = 0.5 * img[r, c] + 0.5 * np.array(COVER_TINT[cov])
        for path_cells in world.get("road_cells", []):
            for r, c in path_cells:
                img[r, c] = (90, 50, 20)
        for r, c in world.get("sites", []):
            img[max(0, r - 2):r + 3, max(0, c - 2):c + 3] = (230, 20, 20)
    img = np.clip(img, 0, 255).astype(np.uint8)[::-1]                     # north up
    Image.fromarray(img).resize((nx * scale, ny * scale), Image.NEAREST).save(path)
