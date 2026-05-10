# main.py  –  The Great Labyrinth
# Entry point.  Game state machine + event handling.

import sys
import pygame

from constants import (
    SCREEN_W, SCREEN_H, FPS, MAX_FLOOR,
    KEY_SHOP, KEY_SKILL, KEY_POTION,
    C_HEAL,
)
from utils import FloatText, center
from stats_collector import StatsCollector
from dungeon import Dungeon
from entities import Player, Enemy
from shop import Shop
from renderer import (
    init_fonts,
    draw_menu,
    draw_class_select,
    draw_playing,
    draw_end,
)

# ── State constants ───────────────────────────────────────────────────────────
ST_MENU    = "menu"
ST_SELECT  = "class_select"
ST_PLAY    = "playing"
ST_DEAD    = "dead"
ST_WIN     = "win"


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("The Great Labyrinth")
        self.clock  = pygame.time.Clock()
        self.fonts  = init_fonts()

        self.stats      = StatsCollector()
        self.state      = ST_MENU
        self.player     : Player | None = None
        self.dungeon    : Dungeon | None = None
        self.enemies    : list[Enemy] = []
        self.floats     : list[FloatText] = []
        self.shop       : Shop | None = None
        self.shop_open  = False
        self.floor      = 1
        self.selected_class = 0
        self.class_list = ["Warrior", "Mage", "Rogue"]
        self.floor_clear_timer = 0

        # UI rects updated by renderer (class select page)
        self._card_rects: list[pygame.Rect] = []
        self._btn_rect  : pygame.Rect | None = None

    # ── Run management ────────────────────────────────────────────────────────
    def _new_run(self, class_name: str):
        """Fresh run: floor 1, brand new player, stats reset."""
        self.floor = 1
        self.stats.reset_run()
        self.player = None          # force Player creation in _load_floor
        self._load_floor(class_name=class_name)
        self.state = ST_PLAY

    def _respawn(self):
        """
        Die → respawn at floor 1.
        Level, XP, ATK, items are KEPT.  HP/MP are restored.
        """
        self.floor = 1
        self.stats.record_encounter(self.floor)
        self.stats.save_to_csv()
        # Restore HP/MP before loading
        self.player.hp = self.player.max_hp
        self.player.mp = self.player.max_mp
        self._load_floor()          # reuse existing player object
        self.state = ST_PLAY

    def _load_floor(self, class_name: str | None = None):
        self.dungeon = Dungeon(self.floor)

        if class_name or self.player is None:
            # New player (fresh run)
            gx, gy = self.dungeon.random_floor_pos(safe_zone=True)
            self.player = Player(gx, gy, class_name or self.class_list[self.selected_class])
        else:
            # Existing player — place in safe zone
            gx, gy = self.dungeon.random_floor_pos(safe_zone=True)
            self.player.gx, self.player.gy = gx, gy
            self.player.px, self.player.py = float(center(gx, gy)[0]), float(center(gx, gy)[1])
            self.player.path      = []
            self.player.wasd_dir  = (0, 0)
            self.player.wasd_timer = 0

        self._spawn_enemies()
        self.floats.clear()
        self.shop_open         = False
        self.floor_clear_timer = 0
        self.shop = Shop() if self.dungeon.shop_pos else None

    def _spawn_enemies(self):
        count = 3 + self.floor // 2
        taken = [(self.player.gx, self.player.gy)]
        self.enemies = []
        for i in range(count):
            gx, gy = self.dungeon.random_floor_pos(
                exclude=taken, avoid_safe=True,
            )
            taken.append((gx, gy))
            is_boss = (self.floor % 5 == 0 and i == count - 1)
            self.enemies.append(Enemy(gx, gy, self.floor, is_boss))

    # ── Main loop ─────────────────────────────────────────────────────────────
    def run(self):
        while True:
            self.clock.tick(FPS)
            self._handle_events()
            self._update()
            self._draw()
            pygame.display.flip()

    # ── Event handling ────────────────────────────────────────────────────────
    def _handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self._quit()

            # ── Keyboard ─────────────────────────────────────────────────────
            if ev.type == pygame.KEYDOWN:
                self._on_keydown(ev.key)

            # ── Mouse ─────────────────────────────────────────────────────────
            if ev.type == pygame.MOUSEBUTTONDOWN:
                self._on_mousedown(ev.button, ev.pos)

    def _on_keydown(self, key: int):
        # Global ESC
        if key == pygame.K_ESCAPE:
            if self.state == ST_PLAY:
                self.stats.save_to_csv()
                self.state = ST_MENU
            elif self.state in (ST_DEAD, ST_WIN):
                self.state = ST_MENU
            return

        if self.state == ST_MENU:
            if key == pygame.K_RETURN:
                self.state = ST_SELECT

        elif self.state == ST_SELECT:
            if key == pygame.K_LEFT:
                self.selected_class = (self.selected_class - 1) % len(self.class_list)
            elif key == pygame.K_RIGHT:
                self.selected_class = (self.selected_class + 1) % len(self.class_list)
            elif key == pygame.K_RETURN:
                self._new_run(self.class_list[self.selected_class])

        elif self.state == ST_DEAD:
            if key == pygame.K_RETURN:
                self._respawn()

        elif self.state == ST_WIN:
            if key == pygame.K_RETURN:
                self.state = ST_SELECT

        elif self.state == ST_PLAY:
            if self.shop_open and self.shop:
                # Shop takes keyboard priority
                if key == KEY_SHOP:
                    self.shop_open = False
                else:
                    self.shop.handle_key(
                        key, self.player, self.stats, self.floor, self.floats,
                    )
                return

            if key == KEY_POTION:
                h = self.player.use_potion(self.stats)
                if h:
                    self.floats.append(
                        FloatText(f"+{h} HP", self.player.px, self.player.py - 30, (80, 255, 130))
                    )
            elif key == KEY_SKILL:
                self.player.use_skill(self.enemies, self.floats, self.stats)
            elif key == KEY_SHOP and self.shop:
                self.shop_open = True

    def _on_mousedown(self, button: int, pos: tuple):
        mx, my = pos

        # ── Class select ──────────────────────────────────────────────────────
        if self.state == ST_SELECT and button == 1:
            for i, rect in enumerate(self._card_rects):
                if rect.collidepoint(mx, my):
                    if self.selected_class == i:
                        self._new_run(self.class_list[i])
                    else:
                        self.selected_class = i
                    return
            if self._btn_rect and self._btn_rect.collidepoint(mx, my):
                self._new_run(self.class_list[self.selected_class])
            return

        # ── Playing ───────────────────────────────────────────────────────────
        if self.state == ST_PLAY:
            if self.shop_open and self.shop:
                # Mouse click on shop item
                if button == 1:
                    self.shop.handle_click(pos, self.player, self.stats, self.floor, self.floats)
                return
            if button == 1:   # Left click → attack
                self.player.attack_nearest(self.enemies, self.floats, self.stats)

    # ── Update ────────────────────────────────────────────────────────────────
    def _update(self):
        if self.state != ST_PLAY:
            return

        p = self.player

        # Cooldown ticks
        if p.atk_cooldown    > 0: p.atk_cooldown    -= 1
        if p.skill_cooldown  > 0: p.skill_cooldown  -= 1
        if p.invincible      > 0: p.invincible      -= 1

        # WASD direction (held keys)
        if not self.shop_open:
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx = -1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx =  1
            if keys[pygame.K_w] or keys[pygame.K_UP]:    dy = -1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy =  1
            if dx != 0:   dy = 0       # prefer horizontal
            p.wasd_dir = (dx, dy)
        else:
            p.wasd_dir = (0, 0)

        p.move_wasd(self.dungeon)

        # Enemy updates
        for e in self.enemies:
            e.update(self.dungeon, p, self.floats, self.stats)

        # Kill resolution
        for e in [en for en in self.enemies if not en.is_alive()]:
            self.stats.add_kill()
            p.money += e.gold_reward
            leveled  = p.gain_xp(e.xp_reward)
            self.floats.append(FloatText(f"+{e.gold_reward}g", e.px, e.py - 10, (255, 210, 60)))
            if leveled:
                self.floats.append(
                    FloatText("LEVEL UP!  HP & MP Restored!", p.px, p.py - 44, (255, 220, 80), 22)
                )
        self.enemies = [e for e in self.enemies if e.is_alive()]

        # Floor-clear countdown
        if not self.enemies and self.floor_clear_timer == 0:
            self.floor_clear_timer = 90
            self.stats.record_encounter(self.floor)

        if self.floor_clear_timer > 0:
            self.floor_clear_timer -= 1
            if self.floor_clear_timer == 0:
                if self.floor >= MAX_FLOOR:
                    self.stats.save_to_csv()
                    self.state = ST_WIN
                else:
                    self.floor += 1
                    self._load_floor()

        # Float text lifecycle
        self.floats = [f for f in self.floats if f.life > 0]
        for f in self.floats:
            f.update()

        # Death check
        if not p.is_alive():
            self.state = ST_DEAD

    # ── Draw ──────────────────────────────────────────────────────────────────
    def _draw(self):
        if self.state == ST_MENU:
            draw_menu(self.screen, self.fonts)

        elif self.state == ST_SELECT:
            rects, btn = draw_class_select(
                self.screen, self.fonts, self.selected_class, self.class_list,
            )
            self._card_rects = rects
            self._btn_rect   = btn

        elif self.state == ST_PLAY:
            draw_playing(self.screen, self.fonts, self)

        elif self.state == ST_DEAD:
            draw_end(self.screen, self.fonts, False, self.player, self.floor)

        elif self.state == ST_WIN:
            draw_end(self.screen, self.fonts, True,  self.player, self.floor)

    # ── Clean exit ────────────────────────────────────────────────────────────
    def _quit(self):
        self.stats.save_to_csv()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
