# entities.py  –  The Great Labyrinth
# Player and Enemy entity classes.

import math
import random
import pygame

from constants import (
    TILE, CLASSES,
    C_WHITE, C_DARK, C_HP_BG, C_HP_BAR,
    C_DMG, C_SKILL, C_HIGHLIGHT, C_HEAL,
    C_ENEMY, C_BOSS,
)
from utils import dist, grid_pos, center, FloatText
from dungeon import bfs_path


# ── Base Entity ───────────────────────────────────────────────────────────────
class Entity:
    def __init__(self, gx: int, gy: int, color: tuple, radius: int = 14):
        self.gx, self.gy   = gx, gy
        self.px, self.py   = center(gx, gy)
        self.color         = color
        self.radius        = radius
        self.hp = self.max_hp = 1
        self.atk           = 5

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> int:
        self.hp = max(0, self.hp - amount)
        return amount

    def draw(self, surf: pygame.Surface):
        cx, cy = int(self.px), int(self.py)
        # drop shadow
        pygame.draw.ellipse(
            surf, (0, 0, 0),
            (cx - self.radius, cy + self.radius - 4, self.radius * 2, 8),
        )
        pygame.draw.circle(surf, self.color, (cx, cy), self.radius)
        pygame.draw.circle(surf, C_WHITE,    (cx, cy), self.radius, 2)
        # HP bar above sprite
        bw = self.radius * 2
        bx = cx - self.radius
        by = cy - self.radius - 8
        pygame.draw.rect(surf, C_HP_BG, (bx, by, bw, 4))
        ratio = self.hp / max(1, self.max_hp)
        pygame.draw.rect(surf, C_HP_BAR, (bx, by, int(bw * ratio), 4))


# ── Player ────────────────────────────────────────────────────────────────────
class Player(Entity):
    MOVE_SPEED = 6   # frames to cross one tile

    def __init__(self, gx: int, gy: int, class_name: str):
        cfg = CLASSES[class_name]
        super().__init__(gx, gy, cfg["color"], radius=16)
        self.class_name  = class_name
        self.hp = self.max_hp = cfg["hp"]
        self.mp = self.max_mp = cfg["mp"]
        self.atk         = cfg["atk"]
        self.base_atk    = cfg["atk"]
        self.defense     = 0
        self.money       = 60
        self.level       = 1
        self.xp          = 0
        self.xp_next     = 30
        self.potions     = 5
        self.inventory   = []
        # movement
        self.path        : list = []
        self.wasd_dir    = (0, 0)
        self.wasd_timer  = 0
        # combat
        self.atk_cooldown   = 0
        self.skill_cooldown = 0
        self.invincible     = 0
        # class-specific ranges
        self.atk_range   = cfg["atk_range"]
        self.skill_mult  = cfg["skill_mult"]

    # ── Movement ──────────────────────────────────────────────────────────────
    def _glide(self):
        """Smoothly slide toward path[0]; pops when reached."""
        if not self.path:
            return
        tx, ty = self.path[0]
        pcx, pcy = center(tx, ty)
        dx, dy = pcx - self.px, pcy - self.py
        d = math.hypot(dx, dy)
        spd = TILE / self.MOVE_SPEED
        if d <= spd + 1:
            self.px, self.py = float(pcx), float(pcy)
            self.gx, self.gy = tx, ty
            self.path.pop(0)
        else:
            self.px += dx / d * spd
            self.py += dy / d * spd

    def move_wasd(self, dungeon):
        """Call every frame; reads self.wasd_dir set by Game._update."""
        if self.wasd_timer > 0:
            self.wasd_timer -= 1
            self._glide()
            return
        dx, dy = self.wasd_dir
        if dx == 0 and dy == 0:
            self._glide()
            return
        nx, ny = self.gx + dx, self.gy + dy
        if dungeon.walkable(nx, ny):
            self.path      = [(nx, ny)]
            self.wasd_timer = self.MOVE_SPEED
        self._glide()

    # ── Combat ────────────────────────────────────────────────────────────────
    def attack_nearest(
        self,
        enemies: list,
        floats: list,
        stats,
        dungeon=None,
    ) -> "Enemy | None":
        if self.atk_cooldown > 0 or not enemies:
            return None
        # Cannot attack while standing in safe zone
        if dungeon and dungeon.is_safe(self.gx, self.gy):
            return None
        nearest = min(enemies, key=lambda e: dist((self.px, self.py), (e.px, e.py)))
        if dist((self.px, self.py), (nearest.px, nearest.py)) < TILE * self.atk_range:
            crit = random.random() < 0.15
            dmg  = int(self.atk * (1.8 if crit else 1.0))
            dmg  = max(1, dmg - getattr(nearest, "defense", 0))
            nearest.take_damage(dmg)
            stats.add_dmg_dealt(dmg)
            self.atk_cooldown = 28
            col = C_HIGHLIGHT if crit else C_DMG
            txt = f"CRIT! -{dmg}" if crit else f"-{dmg}"
            floats.append(FloatText(txt, nearest.px, nearest.py - 20, col))
            return nearest
        return None

    def use_skill(self, enemies: list, floats: list, stats) -> list:
        if self.skill_cooldown > 0 or self.mp < 35:
            return []
        self.mp            -= 35
        self.skill_cooldown = 2000
        hit = []
        for e in enemies:
            if dist((self.px, self.py), (e.px, e.py)) < TILE * 3.5:
                dmg = int(self.atk * self.skill_mult)
                e.take_damage(dmg)
                stats.add_dmg_dealt(dmg)
                floats.append(FloatText(f"-{dmg}", e.px, e.py - 20, C_SKILL))
                hit.append(e)
        return hit

    def use_potion(self, stats) -> int:
        if self.potions > 0 and self.hp < self.max_hp:
            heal = 50
            self.hp      = min(self.max_hp, self.hp + heal)
            self.potions -= 1
            stats.add_potion()
            return heal
        return 0

    # ── Progression ───────────────────────────────────────────────────────────
    def gain_xp(self, amount: int) -> bool:
        self.xp += amount
        leveled  = False
        while self.xp >= self.xp_next:
            self.xp    -= self.xp_next
            self.level += 1
            self.xp_next = int(self.xp_next * 1.4)
            # stat increases on level-up
            self.max_hp += 12
            self.max_mp += 8
            self.atk    += 3
            # full restore on level-up
            self.hp  = self.max_hp
            self.mp  = self.max_mp
            leveled  = True
        return leveled

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surf: pygame.Surface):
        super().draw(surf)
        cx, cy = int(self.px), int(self.py)
        font   = pygame.font.SysFont("Arial", 13, bold=True)
        lbl    = font.render(self.class_name[0], True, C_DARK)
        surf.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))


# ── Enemy ─────────────────────────────────────────────────────────────────────
ENEMY_NAMES = ["Goblin", "Slime", "Bat", "Orc", "Spider", "Troll"]

class Enemy(Entity):
    def __init__(self, gx: int, gy: int, floor: int, is_boss: bool = False):
        col    = C_BOSS if is_boss else C_ENEMY
        radius = 18    if is_boss else 13
        super().__init__(gx, gy, col, radius)
        self.is_boss = is_boss

        # ── Tuned difficulty ──────────────────────────────────────────────────
        # Scale grows slowly; enemies are weaker in early floors.
        scale = 1.0 + floor * 0.18
        if is_boss:
            scale *= 2.8

        self.max_hp = self.hp = int(random.randint(22, 36) * scale)
        self.atk              = int(random.randint(8,  15) * scale)
        self.defense          = 0

        self.xp_reward   = int((14 if is_boss else 5) * scale)
        self.gold_reward = int(random.randint(10, 25)  * scale)

        self.name  = "BOSS" if is_boss else random.choice(ENEMY_NAMES)
        self.state = "idle"
        self.path : list = []
        self.atk_cd      = 0

    # ── AI update (called every frame) ───────────────────────────────────────
    def update(self, dungeon, player: Player, floats: list, stats):
        if not self.is_alive():
            return
        if self.atk_cd > 0:
            self.atk_cd -= 1

        pd = dist((self.px, self.py), (player.px, player.py))

        # Simple 3-state FSM
        if   pd < TILE * 1.4:  self.state = "attack"
        elif pd < TILE * 6.5:  self.state = "chase"
        else:                   self.state = "idle"

        if self.state == "chase":
            # Re-path occasionally
            if not self.path or random.random() < 0.03:
                sg = grid_pos(self.px,       self.py)
                pg = grid_pos(player.px, player.py)
                self.path = bfs_path(dungeon, sg, pg)[1:]
            if self.path:
                tx, ty   = self.path[0]
                pcx, pcy = center(tx, ty)
                dx, dy   = pcx - self.px, pcy - self.py
                d        = math.hypot(dx, dy)
                spd      = TILE / (11 if not self.is_boss else 15)
                if d < spd + 1:
                    self.px, self.py = float(pcx), float(pcy)
                    self.gx, self.gy = tx, ty
                    self.path.pop(0)
                else:
                    self.px += dx / d * spd
                    self.py += dy / d * spd

        elif self.state == "attack":
            if self.atk_cd == 0 and player.invincible == 0:
                # Enemies cannot attack while player is in safe zone
                if not dungeon.is_safe(player.gx, player.gy):
                    dmg = max(1, self.atk - player.defense)
                    player.take_damage(dmg)
                    stats.add_dmg_taken(dmg)
                    self.atk_cd = 55            # slightly slower attack rate
                    floats.append(FloatText(f"-{dmg}", player.px, player.py - 24, C_DMG))

    def draw(self, surf: pygame.Surface):
        super().draw(surf)
        if self.is_boss:
            cx, cy = int(self.px), int(self.py)
            font   = pygame.font.SysFont("Arial", 11, bold=True)
            lbl    = font.render("B", True, C_WHITE)
            surf.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))
