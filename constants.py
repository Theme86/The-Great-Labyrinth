# constants.py  –  The Great Labyrinth
# All shared constants, colours, class/item data

# ── Screen / grid ─────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1100, 700
TILE    = 40
COLS    = 22      # dungeon grid width  (tiles)
ROWS    = 15      # dungeon grid height (tiles)
FPS     = 60
MAX_FLOOR = 20

# ── Palette ───────────────────────────────────────────────────────────────────
C_BG        = (18,  14,  24)
C_WALL      = (45,  38,  60)
C_FLOOR     = (30,  26,  42)
C_FLOOR2    = (34,  30,  46)
C_SAFE      = (25,  45,  25)   # safe-zone tile tint
C_SAFE_BORD = (60, 180,  60)   # safe-zone border
C_PLAYER    = (100, 210, 255)
C_ENEMY     = (230,  80,  80)
C_BOSS      = (230,  60, 230)
C_SHOP_TILE = (60,  50,  20)
C_GOLD      = (255, 210,  60)
C_POTION    = (60,  200, 120)
C_WHITE     = (240, 240, 240)
C_GRAY      = (130, 130, 150)
C_DARK      = (10,   8,  16)
C_HP_BAR    = (220,  60,  60)
C_HP_BG     = (60,   20,  20)
C_MP_BAR    = (60,  120, 220)
C_XP_BAR    = (80,  200,  80)
C_DMG       = (255, 100,  80)
C_HEAL      = (80,  255, 130)
C_SKILL     = (180,  80, 255)
C_PANEL     = (22,  18,  32)
C_ACCENT    = (100, 210, 255)
C_HIGHLIGHT = (255, 220,  80)

# ── Class definitions ─────────────────────────────────────────────────────────
#   atk_range  : how close player must be to auto-attack (in tiles)
#   skill_mult : skill damage multiplier
CLASSES = {
    "Warrior": {
        "hp": 130, "mp": 50,  "atk": 22,
        "atk_range": 1.6,   "skill_mult": 2.0,
        "color": (210, 120,  60),
        "desc":  "Tank — high HP & ATK, close range",
    },
    "Mage": {
        "hp":  70, "mp": 130, "atk": 14,
        "atk_range": 3.5,   "skill_mult": 2.8,
        "color": (130,  80, 255),
        "desc":  "Mage — long range, powerful AoE skill",
    },
    "Rogue": {
        "hp":  95, "mp":  70, "atk": 26,
        "atk_range": 1.8,   "skill_mult": 2.2,
        "color": (60,  220, 160),
        "desc":  "Rogue — highest ATK, medium range",
    },
}

# ── Shop items ────────────────────────────────────────────────────────────────
ITEMS = [
    {"name": "Health Potion", "price": 30, "type": "consumable",
     "effect": "heal",  "value": 50,  "color": C_POTION},
    {"name": "Attack Gem",    "price": 50, "type": "equipment",
     "effect": "atk",   "value": 10,  "color": C_GOLD},
    {"name": "Shield Stone",  "price": 45, "type": "equipment",
     "effect": "def",   "value":  6,  "color": (180, 180, 220)},
    {"name": "Mana Crystal",  "price": 35, "type": "consumable",
     "effect": "mp",    "value": 40,  "color": C_MP_BAR},
    {"name": "Lucky Charm",   "price": 60, "type": "equipment",
     "effect": "luck",  "value":  1,  "color": C_HIGHLIGHT},
]

# ── Key bindings (easy to remap) ──────────────────────────────────────────────
import pygame
KEY_SHOP   = pygame.K_f   # open / close shop  (was S)
KEY_SKILL  = pygame.K_e
KEY_POTION = pygame.K_SPACE
