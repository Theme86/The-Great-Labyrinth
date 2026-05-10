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
    # ── LOW TIER (price 15–40, weight 50–60) ─────────────────────────────────
    {"name": "Small Potion",    "tier": "low",  "price": 15, "weight": 60,
     "type": "consumable", "effect": "heal", "value": 25,
     "color": (80, 200, 120)},
 
    {"name": "Herb Bundle",     "tier": "low",  "price": 20, "weight": 55,
     "type": "consumable", "effect": "heal", "value": 35,
     "color": (100, 210, 100)},
 
    {"name": "Mana Shard",      "tier": "low",  "price": 20, "weight": 55,
     "type": "consumable", "effect": "mp",   "value": 25,
     "color": (80, 130, 220)},
 
    {"name": "Worn Dagger",     "tier": "low",  "price": 25, "weight": 50,
     "type": "equipment",  "effect": "atk",  "value": 4,
     "color": (160, 160, 180)},
 
    {"name": "Cracked Shield",  "tier": "low",  "price": 25, "weight": 50,
     "type": "equipment",  "effect": "def",  "value": 3,
     "color": (140, 140, 160)},
 
    {"name": "Iron Ring",       "tier": "low",  "price": 30, "weight": 50,
     "type": "equipment",  "effect": "atk",  "value": 5,
     "color": (170, 170, 190)},
 
    {"name": "Health Potion",   "tier": "low",  "price": 35, "weight": 55,
     "type": "consumable", "effect": "heal", "value": 50,
     "color": C_POTION},
 
    {"name": "Mana Potion",     "tier": "low",  "price": 35, "weight": 50,
     "type": "consumable", "effect": "mp",   "value": 40,
     "color": (60, 120, 220)},
 
    # ── MID TIER (price 50–90, weight 25–35) ─────────────────────────────────
    {"name": "Steel Sword",     "tier": "mid",  "price": 55, "weight": 30,
     "type": "equipment",  "effect": "atk",  "value": 9,
     "color": (200, 200, 220)},
 
    {"name": "Iron Armor",      "tier": "mid",  "price": 55, "weight": 30,
     "type": "equipment",  "effect": "def",  "value": 8,
     "color": (180, 185, 210)},
 
    {"name": "Attack Gem",      "tier": "mid",  "price": 60, "weight": 28,
     "type": "equipment",  "effect": "atk",  "value": 10,
     "color": C_GOLD},
 
    {"name": "Shield Stone",    "tier": "mid",  "price": 60, "weight": 28,
     "type": "equipment",  "effect": "def",  "value": 8,
     "color": (180, 180, 220)},
 
    {"name": "Mana Crystal",    "tier": "mid",  "price": 65, "weight": 28,
     "type": "consumable", "effect": "mp",   "value": 60,
     "color": C_MP_BAR},
 
    {"name": "Elixir",          "tier": "mid",  "price": 70, "weight": 25,
     "type": "consumable", "effect": "heal", "value": 80,
     "color": (100, 230, 150)},
 
    {"name": "Battle Axe",      "tier": "mid",  "price": 80, "weight": 25,
     "type": "equipment",  "effect": "atk",  "value": 13,
     "color": (210, 170, 80)},
 
    {"name": "Tower Shield",    "tier": "mid",  "price": 85, "weight": 25,
     "type": "equipment",  "effect": "def",  "value": 11,
     "color": (160, 180, 230)},
 
    # ── HIGH TIER (price 100–160, weight 8–15) ────────────────────────────────
    {"name": "Dragon Fang",     "tier": "high", "price": 110, "weight": 12,
     "type": "equipment",  "effect": "atk",  "value": 18,
     "color": (230, 100, 60)},
 
    {"name": "Aegis Plate",     "tier": "high", "price": 110, "weight": 12,
     "type": "equipment",  "effect": "def",  "value": 15,
     "color": (120, 160, 255)},
 
    {"name": "Grand Elixir",    "tier": "high", "price": 130, "weight": 10,
     "type": "consumable", "effect": "heal", "value": 150,
     "color": (60, 255, 160)},
 
    {"name": "Arcane Tome",     "tier": "high", "price": 150, "weight": 8,
     "type": "equipment",  "effect": "atk",  "value": 22,
     "color": (180, 80, 255)},
]
 

# ── Key bindings (easy to remap) ──────────────────────────────────────────────
import pygame
KEY_SHOP   = pygame.K_f   # open / close shop  (was S)
KEY_SKILL  = pygame.K_e
KEY_POTION = pygame.K_SPACE
