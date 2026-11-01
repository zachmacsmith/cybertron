"""Keyed draws (D2-70, D2-173): every random number comes from a stream named by (seed, layer, element), never from a shared
sequence, so changing one element of a world leaves every other element's draws as they were. The key is hashed with sha256, not
Python's hash, so it is the same in every process."""
from __future__ import annotations

import hashlib
import random

import numpy as np


def _int(*parts) -> int:
    return int.from_bytes(hashlib.sha256("|".join(str(p) for p in parts).encode()).digest()[:8], "big")


def rng(*parts) -> random.Random:
    """A Python stream for choices (names, sites, tie-breaks)."""
    return random.Random(_int(*parts))


def nprng(*parts) -> np.random.Generator:
    """A numpy stream for fields (noise lattices, jitter)."""
    return np.random.default_rng(_int(*parts))
