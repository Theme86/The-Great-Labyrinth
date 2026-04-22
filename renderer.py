# renderer.py  –  The Great Labyrinth
# Pure drawing functions.  No game-state mutation here.

import pygame
from constants import (
    SCREEN_W, SCREEN_H, TILE, COLS, ROWS, CLASSES, MAX_FLOOR,
    C_BG, C_WALL, C_FLOOR, C_FLOOR2, C_SAFE, C_SAFE_BORD,
    C_SHOP_TILE, C_GOLD, C_GRAY, C_WHITE, C_DARK,
    C_HP_BAR, C_HP_BG, C_MP_BAR, C_XP_BAR,
    C_ENEMY, C_ACCENT, C_HIGHLIGHT, C_SKILL, C_PANEL,
    KEY_SHOP,
)
from utils import clamp, grid_pos, center


def init_fonts() -> dict:
    return {
        "xl": pygame.font.SysFont("Arial", 36, bold=True),
        "lg": pygame.font.SysFont("Arial", 26, bold=True),
        "md": pygame.font.SysFont("Arial", 18, bold=True),
        "sm": pygame.font.SysFont("Arial", 14),
        "xs": pygame.font.SysFont("Arial", 12),
    }


# ── Menu ──────────────────────────────────────────────────────────────────────
def draw_menu(surf: pygame.Surface, fonts: dict):
    surf.fill(C_BG)
    for y in range(0, SCREEN_H, 40):
        for x in range(0, SCREEN_W, 40):
            if (x // 40 + y // 40) % 2 == 0:
                pygame.draw.rect(surf, (22, 18, 30), (x, y, 40, 40))

    title = fonts["xl"].render("THE GREAT LABYRINTH", True, C_ACCENT)
    surf.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 210))

    sub = fonts["md"].render("A 2D Roguelite Dungeon Adventure", True, C_GRAY)
    surf.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 262))

    btn = fonts["lg"].render("[ ENTER ]  Start Game", True, C_GOLD)
    surf.blit(btn, (SCREEN_W // 2 - btn.get_width() // 2, 350))

    hint = fonts["sm"].render(
        "WASD: Move  |  Right Click: Attack  |  E: Skill  |  SPACE: Potion  |  F: Shop",
        True, C_GRAY,
    )
    surf.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, 450))

    ver = fonts["xs"].render(f"v2.0  —  Reach Floor {MAX_FLOOR} to Win!", True, (60, 55, 80))
    surf.blit(ver, (SCREEN_W // 2 - ver.get_width() // 2, 630))


# ── Class select ──────────────────────────────────────────────────────────────
def draw_class_select(surf: pygame.Surface, fonts: dict, selected: int, class_list: list):
    surf.fill(C_BG)
    t = fonts["lg"].render("Choose Your Class", True, C_ACCENT)
    surf.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 70))

    cw, ch   = 240, 290
    total    = len(class_list) * cw + (len(class_list) - 1) * 30
    ox       = (SCREEN_W - total) // 2
    mx, my   = pygame.mouse.get_pos()

    card_rects = []
    for i, cname in enumerate(class_list):
        cfg     = CLASSES[cname]
        cx      = ox + i * (cw + 30)
        sel     = (i == selected)
        hovered = pygame.Rect(cx, 140, cw, ch).collidepoint(mx, my)
        card_rects.append(pygame.Rect(cx, 140, cw, ch))

        bg = (44, 38, 60) if sel else ((32, 28, 46) if hovered else (22, 18, 32))
        bc = cfg["color"] if sel else (C_ACCENT if hovered else C_GRAY)
        bw = 3 if (sel or hovered) else 1
        pygame.draw.rect(surf, bg, (cx, 140, cw, ch), border_radius=12)
        pygame.draw.rect(surf, bc, (cx, 140, cw, ch), bw, border_radius=12)

        r_size = 42 if (sel or hovered) else 36
        pygame.draw.circle(surf, cfg["color"], (cx + cw // 2, 222), r_size)
        pygame.draw.circle(surf, C_WHITE,      (cx + cw // 2, 222), r_size, 2)
        lbl = fonts["lg"].render(cname[0], True, C_DARK)
        surf.blit(lbl, (cx + cw // 2 - lbl.get_width() // 2, 222 - lbl.get_height() // 2))

        nl = fonts["md"].render(cname, True, C_WHITE if (sel or hovered) else C_GRAY)
        surf.blit(nl, (cx + cw // 2 - nl.get_width() // 2, 272))

        dl = fonts["sm"].render(cfg["desc"], True, cfg["color"])
        surf.blit(dl, (cx + cw // 2 - dl.get_width() // 2, 296))

        for j, (stat, key) in enumerate([
            ("HP",  cfg["hp"]),
            ("ATK", cfg["atk"]),
            ("MP",  cfg["mp"]),
        ]):
            rl = fonts["sm"].render(f"{stat}: {key}", True, C_GRAY)
            surf.blit(rl, (cx + 20, 330 + j * 22))

    # Confirm button
    sel_name = class_list[selected]
    sel_cfg  = CLASSES[sel_name]
    btn_rect = pygame.Rect(SCREEN_W // 2 - 140, 468, 280, 50)
    btn_hov  = btn_rect.collidepoint(mx, my)
    btn_col  = sel_cfg["color"] if btn_hov else (50, 44, 68)
    pygame.draw.rect(surf, btn_col,       btn_rect, border_radius=10)
    pygame.draw.rect(surf, sel_cfg["color"], btn_rect, 2, border_radius=10)
    btn_lbl = fonts["md"].render(f"Play as {sel_name}", True, C_WHITE)
    surf.blit(btn_lbl, (SCREEN_W // 2 - btn_lbl.get_width() // 2, btn_rect.y + 14))

    hint = fonts["sm"].render(
        "Click card to select  |  Click button or ENTER to start", True, C_GRAY,
    )
    surf.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, 530))

    return card_rects, btn_rect


# ── Playing ───────────────────────────────────────────────────────────────────
def draw_playing(surf: pygame.Surface, fonts: dict, game):
    """game is the Game instance; we read its public fields only."""
    surf.fill(C_BG)
    dg = game.dungeon
    p  = game.player

    # Tiles
    for gy in range(ROWS):
        for gx in range(COLS):
            rx, ry = gx * TILE, gy * TILE
            if dg.grid[gy][gx] == 1:
                pygame.draw.rect(surf, C_WALL,      (rx, ry, TILE, TILE))
                pygame.draw.rect(surf, (55, 48, 70), (rx, ry, TILE, TILE), 1)
            else:
                # Safe zone tint
                if dg.is_safe(gx, gy):
                    pygame.draw.rect(surf, C_SAFE, (rx, ry, TILE, TILE))
                else:
                    col = C_FLOOR2 if (gx + gy) % 2 == 0 else C_FLOOR
                    pygame.draw.rect(surf, col, (rx, ry, TILE, TILE))

    # Safe zone border
    if dg.safe_room:
        sr = dg.safe_room
        pygame.draw.rect(
            surf, C_SAFE_BORD,
            (sr.left * TILE, sr.top * TILE, sr.width * TILE, sr.height * TILE),
            2,
        )
        safe_lbl = fonts["xs"].render("SAFE ZONE", True, C_SAFE_BORD)
        surf.blit(safe_lbl, (sr.left * TILE + 4, sr.top * TILE + 2))

    # Shop tile
    if dg.shop_pos:
        sx, sy = dg.shop_pos
        pygame.draw.rect(surf, C_SHOP_TILE, (sx * TILE, sy * TILE, TILE, TILE))
        icon = fonts["sm"].render("$", True, C_GOLD)
        surf.blit(icon, (
            sx * TILE + TILE // 2 - icon.get_width()  // 2,
            sy * TILE + TILE // 2 - icon.get_height() // 2,
        ))
        # Hint when player is near shop tile
        if dg.shop_pos and abs(p.gx - sx) + abs(p.gy - sy) <= 2:
            hint = fonts["sm"].render("[ F ] Open Shop", True, C_GOLD)
            surf.blit(hint, (COLS * TILE // 2 - hint.get_width() // 2, SCREEN_H - 32))

    # Mouse hover tile outline
    mx, my = pygame.mouse.get_pos()
    hx, hy = grid_pos(mx, my)
    if dg.walkable(hx, hy):
        pygame.draw.rect(surf, (255, 255, 255), (hx * TILE, hy * TILE, TILE, TILE), 1)

    # Entities
    for e in game.enemies:
        e.draw(surf)
    p.draw(surf)

    # Float texts
    for f in game.floats:
        f.draw(surf, fonts["sm"])

    # HUD panel
    _draw_hud(surf, fonts, game)

    # Floor-clear banner
    if game.floor_clear_timer > 0:
        alpha = min(255, game.floor_clear_timer * 6)
        msg = fonts["xl"].render(f"Floor {game.floor} Cleared!", True, C_GOLD)
        msg.set_alpha(alpha)
        surf.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2, SCREEN_H // 2 - 30))

    # Shop overlay
    if game.shop_open and game.shop:
        game.shop.draw(surf, p, fonts)


def _draw_hud(surf: pygame.Surface, fonts: dict, game):
    p  = game.player
    ox = COLS * TILE + 10
    bw = SCREEN_W - COLS * TILE - 20

    # Panel background
    pygame.draw.rect(surf, C_PANEL, (COLS * TILE, 0, SCREEN_W - COLS * TILE, SCREEN_H))
    pygame.draw.line(surf, C_ACCENT, (COLS * TILE, 0), (COLS * TILE, SCREEN_H), 2)

    def bar(label, val, mx_val, col, y):
        lbl = fonts["xs"].render(label, True, C_GRAY)
        surf.blit(lbl, (ox, y))
        pygame.draw.rect(surf, (30, 28, 40), (ox, y + 14, bw, 10), border_radius=3)
        filled = int(bw * clamp(val / max(1, mx_val), 0, 1))
        pygame.draw.rect(surf, col, (ox, y + 14, filled, 10), border_radius=3)
        num = fonts["xs"].render(f"{val}/{mx_val}", True, C_WHITE)
        surf.blit(num, (ox + bw - num.get_width(), y + 14))

    # Class + level
    cn = fonts["md"].render(
        f"{p.class_name}  Lv{p.level}", True, CLASSES[p.class_name]["color"],
    )
    surf.blit(cn, (ox, 10))
    bar("HP", p.hp,  p.max_hp,  C_HP_BAR, 36)
    bar("MP", p.mp,  p.max_mp,  C_MP_BAR, 64)
    bar("XP", p.xp,  p.xp_next, C_XP_BAR, 92)

    y = 130
    for line in [
        f"ATK: {p.atk}",
        f"DEF: {p.defense}",
        f"Gold: {p.money}g",
        f"Potions: {p.potions}",
    ]:
        lbl = fonts["sm"].render(line, True, C_WHITE)
        surf.blit(lbl, (ox, y))
        y += 22

    fl = fonts["lg"].render(f"Floor  {game.floor}/{MAX_FLOOR}", True, C_ACCENT)
    surf.blit(fl, (ox, y + 10))
    y += 44

    el = fonts["sm"].render(f"Enemies: {len(game.enemies)}", True, C_ENEMY)
    surf.blit(el, (ox, y))
    y += 26

    # Safe zone indicator
    if game.dungeon.is_safe(p.gx, p.gy):
        safe_ind = fonts["sm"].render("[ SAFE ZONE ]", True, (80, 220, 80))
        surf.blit(safe_ind, (ox, y))
        y += 20

    # Skill cooldown
    if p.skill_cooldown > 0:
        cd_s = (p.skill_cooldown + 59) // 60
        cl = fonts["xs"].render(f"Skill CD: {cd_s}s", True, C_SKILL)
        surf.blit(cl, (ox, y))
        y += 18

    # Controls hint (bottom of panel)
    y = SCREEN_H - 130
    for line in [
        "WASD: Move",
        "RClick: Attack",
        "E: Area Skill",
        "SPACE: Potion",
        "F: Shop",
        "ESC: Menu",
    ]:
        lbl = fonts["xs"].render(line, True, (70, 65, 90))
        surf.blit(lbl, (ox, y))
        y += 20


# ── End screen ────────────────────────────────────────────────────────────────
def draw_end(surf: pygame.Surface, fonts: dict, win: bool, player, floor: int):
    surf.fill(C_BG)
    col   = C_GOLD if win else (220, 60, 60)
    title = ("YOU WIN!" if win else "GAME OVER")
    t     = fonts["xl"].render(title, True, col)
    surf.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 180))

    if player:
        for i, line in enumerate([
            f"Floor Reached : {floor}/{MAX_FLOOR}",
            f"Level          : {player.level}",
            f"Gold           : {player.money}",
            f"ATK            : {player.atk}",
        ]):
            lbl = fonts["md"].render(line, True, C_WHITE)
            surf.blit(lbl, (SCREEN_W // 2 - lbl.get_width() // 2, 280 + i * 36))

    if not win:
        note = fonts["sm"].render(
            "You respawn at Floor 1 — level & items kept!", True, C_ACCENT,
        )
        surf.blit(note, (SCREEN_W // 2 - note.get_width() // 2, 440))

    h = fonts["md"].render("Press ESC  to Menu  |  ENTER  to Retry", True, C_GRAY)
    surf.blit(h, (SCREEN_W // 2 - h.get_width() // 2, 490))

    saved = fonts["xs"].render(
        "Run data saved to combat_log.csv & shop_log.csv", True, (60, 55, 80),
    )
    surf.blit(saved, (SCREEN_W // 2 - saved.get_width() // 2, 540))
