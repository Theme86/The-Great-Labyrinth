# shop.py  –  The Great Labyrinth
# Shop UI — opened with KEY_SHOP (F key).  Supports keyboard 1-4 AND mouse click.

import random
import pygame

from constants import (
    SCREEN_W, SCREEN_H, ITEMS,
    C_PANEL, C_ACCENT, C_GOLD, C_GRAY, C_WHITE, C_WHITE,
    C_HEAL, C_HIGHLIGHT, C_MP_BAR, C_POTION,
)
from utils import FloatText


class Shop:
    ITEM_H  = 64
    ITEM_W  = 440
    OW, OH  = 520, 400

    def __init__(self):
        self.total_spent = 0
        self.inventory = random.sample(ITEMS, min(4, len(ITEMS)))
        self.bought    : set[int] = set()
        # Pre-compute item rects (relative to panel origin; resolved in draw)
        self._item_rects: list[pygame.Rect] = []

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surf: pygame.Surface, player, fonts: dict):
        ow, oh = self.OW, self.OH
        ox     = (SCREEN_W - ow) // 2
        oy     = (SCREEN_H - oh) // 2

        # Panel background
        pygame.draw.rect(surf, C_PANEL, (ox, oy, ow, oh), border_radius=14)
        pygame.draw.rect(surf, C_ACCENT,(ox, oy, ow, oh), 2, border_radius=14)

        # Title
        title = fonts["lg"].render("   SHOP   ", True, C_GOLD)
        surf.blit(title, (ox + ow // 2 - title.get_width() // 2, oy + 12))

        # Gold
        gold_lbl = fonts["sm"].render(f"Gold: {player.money}", True, C_GOLD)
        surf.blit(gold_lbl, (ox + ow - gold_lbl.get_width() - 16, oy + 14))

        mx, my = pygame.mouse.get_pos()
        self._item_rects.clear()

        for i, item in enumerate(self.inventory):
            ix = ox + 30
            iy = oy + 68 + i * (self.ITEM_H + 8)
            rect = pygame.Rect(ix, iy, self.ITEM_W, self.ITEM_H)
            self._item_rects.append(rect)

            bought  = i in self.bought
            hovered = rect.collidepoint(mx, my) and not bought
            affordable = player.money >= item["price"]

            bg  = (22, 20, 32) if bought else ((38, 34, 54) if hovered else (28, 26, 40))
            bc  = C_GRAY if bought else (item["color"] if (hovered or affordable) else C_GRAY)
            bw  = 2 if hovered else 1
            pygame.draw.rect(surf, bg,  rect, border_radius=8)
            pygame.draw.rect(surf, bc,  rect, bw, border_radius=8)

            # item icon circle
            pygame.draw.circle(surf, item["color"], (ix + 36, iy + self.ITEM_H // 2), 20)
            pygame.draw.circle(surf, C_WHITE,       (ix + 36, iy + self.ITEM_H // 2), 20, 2)

            name_col = C_GRAY if bought else C_WHITE
            nlbl = fonts["md"].render(item["name"], True, name_col)
            surf.blit(nlbl, (ix + 66, iy + 10))

            eff  = f'+{item["value"]} {item["effect"].upper()}'
            elbl = fonts["sm"].render(eff, True, C_GRAY)
            surf.blit(elbl, (ix + 66, iy + 36))

            price_col = C_GRAY if (bought or not affordable) else C_GOLD
            plbl = fonts["md"].render(f'{item["price"]}g', True, price_col)
            surf.blit(plbl, (ix + self.ITEM_W - 70, iy + 20))

            if not bought:
                kk = fonts["sm"].render(f'[{i + 1}]', True, C_ACCENT)
                surf.blit(kk, (ix + self.ITEM_W - 30, iy + 22))

        hint = fonts["sm"].render(
            "Click or press 1-4 to buy   |   F to close",
            True, C_GRAY,
        )
        surf.blit(hint, (ox + ow // 2 - hint.get_width() // 2, oy + oh - 26))

    # ── Input: keyboard ───────────────────────────────────────────────────────
    def handle_key(self, key: int, player, stats, floor: int, floats: list):
        idx_map = {
            pygame.K_1: 0, pygame.K_2: 1,
            pygame.K_3: 2, pygame.K_4: 3,
        }
        idx = idx_map.get(key)
        if idx is not None:
            self._try_buy(idx, player, stats, floor, floats)

    # ── Input: mouse click (call on MOUSEBUTTONDOWN when shop open) ───────────
    def handle_click(self, pos: tuple, player, stats, floor: int, floats: list):
        for i, rect in enumerate(self._item_rects):
            if rect.collidepoint(pos):
                self._try_buy(i, player, stats, floor, floats)
                return

    # ── Shared purchase logic ─────────────────────────────────────────────────
    def _try_buy(self, idx: int, player, stats, floor: int, floats: list):
        if idx >= len(self.inventory) or idx in self.bought:
            return
        item = self.inventory[idx]
        if player.money < item["price"]:
            return
        player.money -= item["price"]
        self.bought.add(idx)
        self.total_spent += item["price"]

        fx, fy = player.px, player.py - 30
        if item["effect"] == "heal":
            player.hp = min(player.max_hp, player.hp + item["value"])
            floats.append(FloatText(f'+{item["value"]} HP',  fx, fy, C_HEAL))
        elif item["effect"] == "atk":
            player.atk += item["value"]
            floats.append(FloatText(f'+{item["value"]} ATK!', fx, fy, C_HIGHLIGHT))
        elif item["effect"] == "def":
            player.defense += item["value"]
            floats.append(FloatText(f'+{item["value"]} DEF!', fx, fy, (180, 200, 255)))
        elif item["effect"] == "mp":
            player.mp = min(player.max_mp, player.mp + item["value"])
            floats.append(FloatText(f'+{item["value"]} MP!',  fx, fy, (100, 160, 255)))
        elif item["effect"] == "luck":
            player.potions += 1
            floats.append(FloatText('+1 Potion!', fx, fy, C_POTION))
