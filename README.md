# The Great Labyrinth

## Project Description

- **Project by:** *(Krittin kongsiang)*
- **Game Genre:** Roguelite, Action, Dungeon Crawler
- **Course:** Computer Programming II (01219116 / 01219117) — 2026/2, Section 450

The Great Labyrinth is a 2D top-down roguelite dungeon game built with Python and Pygame.
The player chooses a class (Warrior, Mage, or Rogue), descends through procedurally generated floors,
fights enemies, collects gold, and visits shops to grow stronger.
Every run records combat and economy data to CSV files for statistical analysis.

---

## Installation

Clone this repository:

```sh
git clone https://github.com/<username>/great-labyrinth.git
cd great-labyrinth
```

**Windows:**

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Mac / Linux:**

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Running Guide

After activating the virtual environment, run the game with:

**Windows:**

```bat
python main.py
```

**Mac / Linux:**

```sh
python3 main.py
```

To view the data visualization dashboard (after playing at least one run):

**Windows:**

```bat
python data_analysis.py
```

**Mac / Linux:**

```sh
python3 data_analysis.py
```

---

## Tutorial / Usage

### Controls

| Input | Action |
|-------|--------|
| `W` / `A` / `S` / `D` | Move up / left / down / right |
| Arrow Keys | Move (alternative) |
| Left Click | Attack nearest enemy |
| `E` | Use area skill (costs MP) |
| `Space` | Use health potion |
| `F` | Open / close shop (available on every floors ) |
| `ESC` | Return to main menu |

### Game Flow

1. Launch `main.py` — the main menu appears.
2. Press **Enter** to go to the class selection screen.
3. **Click a class card** to highlight it, then click the **"Play as …"** button (or press Enter) to start.
4. Explore the dungeon with WASD. The **green-tinted room** at the start of each floor is the **Safe Zone** — enemies cannot attack you there.
5. Right-click to attack enemies. Kill all enemies to advance to the next floor.
6. Shop  — press `F` to open it and click to buy items.
7. Reach **Floor 20** to win. If you die, you respawn at Floor 1 with your level and items kept.

---

## Game Features

- **3 Playable Classes** — Warrior (high HP/ATK, melee), Mage (long range, strong AoE), Rogue (highest ATK, medium range); each has unique stats and attack range.
- **Procedural Dungeon Generation** — every floor is randomly generated using seeded room placement and L-shaped corridors.
- **Safe Zone** — the first room of every floor is a protected spawn area; enemies cannot attack the player inside it.
- **Enemy AI** — finite-state machine (idle → chase → attack) with BFS pathfinding.
- **Boss Floors** — a stronger boss enemy spawns on every 5th floor.
- **Shop System** — use mouse click to purchase.
- **Level-Up System** — gaining enough XP levels up the player, fully restoring HP and MP and increasing stats.
- **Death & Respawn** — dying returns the player to Floor 1; level, gold, and items are preserved.
- **Data Collection** — every floor clear and shop visit is logged to `combat_log.csv` and `shop_log.csv`.
- **Statistical Dashboard** — `data_analysis.py` generates 5 charts from collected run data.

---

## Known Bugs

- Enemies can occasionally overlap each other in narrow corridors.
- The shop tile `$` icon may not render correctly on some non-UTF-8 terminal fonts .


---

## Unfinished Works

- Sound effects and background music are not yet implemented.
- skill animations for the player class (currently uses instant-hit attack).
- skill is too overpower(op) not balanced yet

---

