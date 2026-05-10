# Project Description

## 1. Project Overview

- **Project Name:** The Great Labyrinth

- **Brief Description:**  
  The Great Labyrinth is a 2D top-down roguelite dungeon-crawler game developed in Python using the Pygame library. Players select one of three character classes — Warrior, Mage, or Rogue — and descend through up to 20 procedurally generated dungeon floors. Each floor is populated with randomly spawned enemies and optional shops. The player must defeat all enemies on a floor to advance, collecting gold and experience points along the way to grow stronger with each run.

  The project also includes a statistical data layer: every combat encounter and shop visit is recorded to CSV files, and a separate analysis script generates interactive charts to visualise player behaviour and combat performance across multiple runs. This dual-purpose design makes the project both a playable game and a small data-collection system.

- **Problem Statement:**  
  Roguelite games generate large volumes of moment-to-moment gameplay data (damage dealt, resources spent, enemies killed) that are rarely surfaced to the player or developer. This project explores how to embed lightweight telemetry directly into a game loop, making run data immediately available for analysis without requiring an external database or server.

- **Target Users:**  
  - Students and hobbyists learning Python game development.  
  - Game designers or researchers interested in player-behaviour data at a small scale.  
  - Anyone looking for a quick, replayable dungeon-crawler experience.

- **Key Features:**
  - Three distinct playable classes with different HP, ATK, and attack-range profiles.
  - Procedural dungeon generation (seeded room placement + BFS-connected corridors) for a unique layout every run.
  - Safe Zone on every floor — enemies cannot attack the player in the first room.
  - Enemy AI driven by a finite-state machine (idle → chase → attack) with BFS pathfinding.
  - Boss enemy on every 5th floor.
  - Shop system on floors 5, 10, 15, 20 — supports keyboard and mouse input.
  - Level-up system that fully restores HP and MP on each level gained.
  - Death-respawn mechanic: respawn at Floor 1 with level and items kept.
  - Automatic CSV logging of combat and shop data after every run.
  - Statistical dashboard (`data_analysis.py`) with 5 chart types.

- **Screenshots:**  
  *(See `screenshots/gameplay/` and `screenshots/visualization/` folders in this repository.)*

- **Proposal:** [proposal.pdf](./proposal.pdf)

- **YouTube Presentation:** *(https://www.youtube.com/watch?v=uK29S5CFjsc)*

---

## 2. Concept

### 2.1 Background

Roguelite games have long been popular for their high replayability: procedural generation and permadeath ensure that no two runs feel identical. Games such as *Pixel Dungeon* demonstrate that even a simple, single-developer roguelike can deliver deep strategic choices through class selection, item management.

This project was inspired by the desire to combine that familiar roguelite loop with lightweight in-game telemetry. Most commercial games use proprietary analytics pipelines hidden from developers and players alike. Here, the data collection is transparent, file-based (CSV), and immediately usable — aligning with the course's emphasis on data processing in Python.

The core problem the game addresses is **engagement through meaningful choice**: which class to pick, which items to buy, when to use a potion. Making those choices visible in post-run charts creates a feedback loop that encourages repeated play and reflection.

### 2.2 Objectives

- Build a fully playable 2D roguelite game with at least three classes, procedural floors, a shop, and a boss encounter.
- Implement a clean object-oriented architecture separating game logic, rendering, dungeon generation, entities, and data collection into distinct modules.
- Collect per-floor combat statistics (enemies killed, damage dealt, damage taken, potions used) and per-shop spending data automatically during gameplay.
- Export collected data to CSV files and visualise them with at least five chart types (histogram, bar chart, box plot, scatter plot, line chart).
- Demonstrate good software-engineering practices: modular file structure, a `.gitignore`, a `requirements.txt`, and clear documentation.

---

## 3. UML Class Diagram

The diagram below summarises the key classes and their relationships.


*(A PDF version of the UML diagram is attached as `UML.pdf` in this repository.)*

---

## 4. Object-Oriented Programming Implementation

| Class | File | Description |
|-------|------|-------------|
| `Game` | `main.py` | Central state machine. Owns all game objects, drives the main loop, dispatches events, and transitions between states (menu → class select → playing → dead/win). |
| `Entity` | `entities.py` | Abstract base class for all in-world objects. Stores position (grid + pixel), HP, ATK, colour, and radius. Implements `take_damage()` and a generic `draw()` with HP bar. |
| `Player` | `entities.py` | Extends `Entity`. Adds class-specific stats (MP, XP, level, potions, defense), smooth WASD tile-by-tile movement (`move_wasd()`), attack with range check (`attack_nearest()`), area skill (`use_skill()`), potion use, and level-up logic that fully restores HP/MP. |
| `Enemy` | `entities.py` | Extends `Entity`. Implements a three-state FSM (idle / chase / attack) updated each frame. Uses BFS pathfinding to navigate toward the player. Cannot attack the player inside the safe zone. Scales stats with floor number. |
| `Dungeon` | `dungeon.py` | Procedurally generates one floor: places random rooms, connects them with L-corridors, designates the first room as a safe zone, and optionally places a shop tile. Provides `walkable()`, `is_safe()`, and `random_floor_pos()` helpers. |
| `Shop` | `shop.py` | Renders the shop overlay and handles item purchases via keyboard (1–4) and mouse click. Calls `StatsCollector.record_shop()` on each purchase and applies item effects to the player. |
| `StatsCollector` | `stats_collector.py` | Accumulates per-encounter data (kills, damage dealt/taken, potions used) and per-shop spending. Exports two CSV files (`combat_log.csv`, `shop_log.csv`) at run end. |
| `FloatText` | `utils.py` | Lightweight floating damage / heal number that rises and fades over ~70 frames. |

**Design patterns used:**
- **State Machine** — `Game.state` string drives which update/draw branch executes each frame.
- **Finite-State Machine (FSM)** — `Enemy.state` (idle / chase / attack) controls AI behaviour.
- **Separation of Concerns** — rendering (`renderer.py`) is fully decoupled from game logic (`main.py`, `entities.py`); constants live in one file (`constants.py`).

---

## 5. Statistical Data

### 5.1 Data Recording Method

Data is collected automatically during gameplay by the `StatsCollector` class. Two CSV files are written to the working directory at the end of every run (death or floor-20 clear):

| File | Trigger | Contents |
|------|---------|----------|
| `combat_log.csv` | End of each floor (all enemies defeated) | run_id, floor, timestamp, enemies_killed, damage_taken, damage_dealt, potions_used |
| `shop_log.csv` | Each item purchased in the shop | run_id, floor, timestamp, money_spent |

The `data_analysis.py` script reads both files and generates five charts using Matplotlib.

### 5.2 Data Features

| Feature | Type | Description |
|---------|------|-------------|
| `enemies_killed` | int | Number of enemies defeated in one floor encounter |
| `damage_taken` | int | Total HP lost by the player during one floor |
| `damage_dealt` | int | Total damage the player inflicted during one floor |
| `potions_used` | int | Number of potions consumed during one floor |
| `money_spent` | int | Gold spent in a single shop visit |

**Visualisations generated by `data_analysis.py`:**

1. **Histogram** — Distribution of `enemies_killed` per encounter; shows whether floors tend to be light or heavy on enemies.
2. **Bar Chart** — Average `money_spent` per shop visit across all recorded shop floors; reveals spending behaviour.
3. **Box Plot** — Spread and outliers of `damage_taken` per encounter; highlights unusually difficult floors.
4. **Scatter Plot** — `damage_dealt` vs `damage_taken` per floor; visualises player efficiency (high dealt, low taken = good run).
5. **Line Chart** — `potions_used` across sequential encounters; shows how resource consumption changes as the run progresses.

---

## 6. Changed Proposed Features

| Original Proposal | Final Implementation | Reason for Change |
|---|---|---|
| Left-click to move (pathfinding) | WASD tile-by-tile movement | More responsive and intuitive for a dungeon crawler; BFS pathfinding is retained for enemy AI only |
| Shop opened with `S` key | Shop opened with `F` key | `S` is used for downward movement; separating the bindings avoids accidental shop activation |
| Player respawns with full reset | Player respawns at Floor 1 with level/items kept | Reduces frustration while maintaining some consequence for death |
| No safe zone | Safe Zone added to first room of every floor | Gives players a guaranteed breathing space when entering a new floor |

---


