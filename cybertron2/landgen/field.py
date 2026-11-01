"""The grid of cells and the noise the land is shaped from.

The cells are a square grid of spacing `km` (stage 1 §2: about 150 m, a unit of size of about 2 ha a cell), each cell's point
jittered within it, with its eight neighbours. Fields are 2-D numpy arrays indexed [row, col]; row 0 is the south edge, so a cell's
(x, y) in km is (col + jitter, row + jitter) x km. Noise is gradient noise on a lattice whose gradients are keyed draws, summed
over octaves (fBm), optionally warped and ridged, all vectorised.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cybertron2.landgen import keyed

N8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]      # the eight neighbours, as (drow, dcol)
D8 = np.array([np.hypot(a, b) for a, b in N8])                                     # their distances in cells


@dataclass
class Grid:
    seed: int
    size_km: float                     # the window's side
    km: float                          # cell spacing
    ny: int
    nx: int
    x: np.ndarray                      # km, each cell's point
    y: np.ndarray

    @property
    def shape(self):
        return (self.ny, self.nx)

    def cell(self, xkm: float, ykm: float) -> tuple[int, int]:
        """The cell holding a point in km (clamped to the window)."""
        c = int(np.clip(round(xkm / self.km), 0, self.nx - 1))
        r = int(np.clip(round(ykm / self.km), 0, self.ny - 1))
        return r, c

    def shifted(self, a: np.ndarray, dr: int, dc: int, fill=np.nan) -> np.ndarray:
        """`a` moved so each cell sees its neighbour at (dr, dc); cells off the edge get `fill`."""
        out = np.full(a.shape, fill, dtype=float)
        r0, r1 = max(0, -dr), self.ny - max(0, dr)
        c0, c1 = max(0, -dc), self.nx - max(0, dc)
        out[r0:r1, c0:c1] = a[r0 + dr:r1 + dr, c0 + dc:c1 + dc]
        return out


def grid(seed: int, size_km: float, km: float) -> Grid:
    n = int(round(size_km / km)) + 1
    g = keyed.nprng(seed, "grid", "jitter")
    jx, jy = g.uniform(-0.35, 0.35, (n, n)), g.uniform(-0.35, 0.35, (n, n))
    cols, rows = np.meshgrid(np.arange(n), np.arange(n))
    return Grid(seed, size_km, km, n, n, (cols + jx) * km, (rows + jy) * km)


def _gradient(seed, key, x, y, freq) -> np.ndarray:
    """Gradient noise at points (x, y) in km for a lattice of `freq` cycles a km; about -1 to 1."""
    fx, fy = x * freq, y * freq
    x0, y0 = np.floor(fx).astype(int), np.floor(fy).astype(int)
    tx, ty = fx - x0, fy - y0
    lo_x, lo_y = int(x0.min()), int(y0.min())
    w, h = int(x0.max()) - lo_x + 2, int(y0.max()) - lo_y + 2
    ang = keyed.nprng(seed, "noise", key, freq).uniform(0, 2 * np.pi, (h, w))
    gx, gy = np.cos(ang), np.sin(ang)

    def dot(ix, iy, dx, dy):
        return gx[iy - lo_y, ix - lo_x] * dx + gy[iy - lo_y, ix - lo_x] * dy

    s = lambda t: t * t * t * (t * (t * 6 - 15) + 10)
    n00, n10 = dot(x0, y0, tx, ty), dot(x0 + 1, y0, tx - 1, ty)
    n01, n11 = dot(x0, y0 + 1, tx, ty - 1), dot(x0 + 1, y0 + 1, tx - 1, ty - 1)
    u, v = s(tx), s(ty)
    return 1.41 * ((n00 * (1 - u) + n10 * u) * (1 - v) + (n01 * (1 - u) + n11 * u) * v)


def fbm(seed, key, x, y, scale_km: float, octaves: int = 5, gain: float = 0.5, ridged: bool = False) -> np.ndarray:
    """Fractal noise of feature size `scale_km`, about -1 to 1 (ridged: 0 to 1, peaked along lines)."""
    out, amp, tot = np.zeros_like(x, dtype=float), 1.0, 0.0
    for o in range(octaves):
        n = _gradient(seed, f"{key}:{o}", x, y, (2 ** o) / scale_km)
        out += amp * ((1 - np.abs(n)) ** 2 if ridged else n)
        tot += amp
        amp *= gain
    return out / tot


def warped(seed, key, x, y, scale_km: float, warp_km: float, **kw) -> np.ndarray:
    """fBm sampled at points displaced by another noise (domain warping): less regular shapes."""
    wx = fbm(seed, f"{key}:wx", x, y, scale_km * 1.5, octaves=3) * warp_km
    wy = fbm(seed, f"{key}:wy", x, y, scale_km * 1.5, octaves=3) * warp_km
    return fbm(seed, key, x + wx, y + wy, scale_km, **kw)


def slope_deg(g: Grid, h: np.ndarray) -> np.ndarray:
    """Slope in degrees from the steepest of the eight neighbours."""
    best = np.zeros(g.shape)
    for (dr, dc), d in zip(N8, D8):
        nb = g.shifted(h, dr, dc, fill=np.nan)
        drop = np.abs(np.nan_to_num(nb - h, nan=0.0)) / (d * g.km * 1000.0)
        best = np.maximum(best, drop)
    return np.degrees(np.arctan(best))


def box_mean(a: np.ndarray, radius: int) -> np.ndarray:
    """The mean of `a` over a square of side 2r+1 round each cell (summed-area table), edges clamped."""
    p = np.pad(a.astype(float), radius, mode="edge")
    c = p.cumsum(0).cumsum(1)
    c = np.pad(c, ((1, 0), (1, 0)))
    k = 2 * radius + 1
    s = c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]
    return s / (k * k)
