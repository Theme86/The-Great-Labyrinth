# utils.py  –  The Great Labyrinth
# Shared helper functions

import math
import pygame
from constants import TILE


def dist(a, b):
    """Euclidean distance between two (x,y) points."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def grid_pos(px, py):
    """Convert pixel position to tile grid coordinates."""
    return int(px // TILE), int(py // TILE)


def center(gx, gy):
    """Return pixel centre of a grid tile."""
    return gx * TILE + TILE // 2, gy * TILE + TILE // 2


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def draw_bar(surf, x, y, w, h, value, maximum, fg, bg=(30, 28, 40)):
    """Draw a filled progress bar."""
    pygame.draw.rect(surf, bg, (x, y, w, h), border_radius=3)
    filled = int(w * clamp(value / max(1, maximum), 0, 1))
    if filled > 0:
        pygame.draw.rect(surf, fg, (x, y, filled, h), border_radius=3)


# ── Floating damage / heal text ───────────────────────────────────────────────
class FloatText:
    def __init__(self, text, x, y, color, size=18):
        self.text  = text
        self.x     = float(x)
        self.y     = float(y)
        self.color = color
        self.size  = size
        self.life  = 70
        self.vy    = -1.3

    def update(self):
        self.life -= 1
        self.y    += self.vy

    def draw(self, surf, font):
        alpha = int(255 * (self.life / 70))
        s = font.render(self.text, True, self.color)
        s.set_alpha(alpha)
        surf.blit(s, (int(self.x - s.get_width() // 2), int(self.y)))
