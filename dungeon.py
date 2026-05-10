# dungeon.py  –  The Great Labyrinth
# Procedural dungeon generator with safe-zone room.

import random
import pygame
from collections import deque
from constants import COLS, ROWS, TILE, MAX_FLOOR
from utils import center


# ── BFS pathfinding (used by enemies too) ────────────────────────────────────
def bfs_path(dungeon, start, goal):
    sx, sy = start
    gx, gy = goal
    if not dungeon.walkable(gx, gy):
        return []
    visited = {(sx, sy): None}
    q = deque([(sx, sy)])
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while q:
        cx, cy = q.popleft()
        if (cx, cy) == (gx, gy):
            path, cur = [], (gx, gy)
            while cur:
                path.append(cur)
                cur = visited[cur]
            return path[::-1]
        for dx, dy in dirs:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) not in visited and dungeon.walkable(nx, ny):
                visited[(nx, ny)] = (cx, cy)
                q.append((nx, ny))
    return []


class Dungeon:
    """
    Generates a dungeon for one floor.

    Attributes
    ----------
    grid      : 2-D list  (0 = floor, 1 = wall)
    rooms     : list of pygame.Rect  (tile units)
    shop_pos  : (gx, gy) or None  — tile where the shop NPC stands
    safe_room : pygame.Rect or None — the designated safe room
    safe_tiles: set of (gx, gy) inside safe_room
    """

    def __init__(self, floor: int, seed: int | None = None):
        self.floor     = floor
        self.seed      = seed if seed is not None else random.randint(0, 99_999)
        self.grid      = [[1] * COLS for _ in range(ROWS)]
        self.rooms     = []
        self.shop_pos  = None
        self.safe_room = None
        self.safe_tiles: set[tuple[int, int]] = set()
        random.seed(self.seed)
        self._generate()

    # ── Generation ────────────────────────────────────────────────────────────
    def _generate(self):
        rooms: list[pygame.Rect] = []
        attempts = 0

        # 1. Place random rooms
        while len(rooms) < 8 and attempts < 300:
            attempts += 1
            w = random.randint(3, 6)
            h = random.randint(3, 5)
            x = random.randint(1, COLS - w - 1)
            y = random.randint(1, ROWS - h - 1)
            r = pygame.Rect(x, y, w, h)
            if any(r.inflate(2, 2).colliderect(ro) for ro in rooms):
                continue
            rooms.append(r)
            for cy in range(y, y + h):
                for cx in range(x, x + w):
                    self.grid[cy][cx] = 0

        # 2. Connect rooms with L-corridors
        for i in range(1, len(rooms)):
            ax, ay = rooms[i - 1].centerx, rooms[i - 1].centery
            bx, by = rooms[i].centerx,     rooms[i].centery
            if random.random() < 0.5:
                for cx in range(min(ax, bx), max(ax, bx) + 1):
                    self.grid[ay][cx] = 0
                for cy in range(min(ay, by), max(ay, by) + 1):
                    self.grid[cy][bx] = 0
            else:
                for cy in range(min(ay, by), max(ay, by) + 1):
                    self.grid[cy][ax] = 0
                for cx in range(min(ax, bx), max(ax, bx) + 1):
                    self.grid[by][cx] = 0

        self.rooms = rooms
        if not rooms:
            return

        # 3. Designate first room as safe zone (spawn room)
        self.safe_room = rooms[0]
        for cy in range(rooms[0].top, rooms[0].bottom):
            for cx in range(rooms[0].left, rooms[0].right):
                self.safe_tiles.add((cx, cy))

        # 4. Shop
        sr = rooms[-1]
        self.shop_pos = (sr.centerx, sr.centery)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def walkable(self, gx: int, gy: int) -> bool:
        return 0 <= gx < COLS and 0 <= gy < ROWS and self.grid[gy][gx] == 0

    def is_safe(self, gx: int, gy: int) -> bool:
        return (gx, gy) in self.safe_tiles

    def random_floor_pos(
        self,
        exclude: list[tuple[int, int]] | None = None,
        safe_zone: bool = False,
        avoid_safe: bool = False,
    ) -> tuple[int, int]:
        """
        Return a random walkable tile.
        safe_zone=True  → must be inside safe_tiles
        avoid_safe=True → must NOT be inside safe_tiles
        """
        exclude = exclude or []
        candidates = [
            (r.left + cx, r.top + cy)
            for r in self.rooms
            for cx in range(r.width)
            for cy in range(r.height)
            if self.walkable(r.left + cx, r.top + cy)
        ]
        if safe_zone:
            candidates = [c for c in candidates if c in self.safe_tiles]
        elif avoid_safe:
            candidates = [c for c in candidates if c not in self.safe_tiles]
        candidates = [c for c in candidates if c not in exclude]
        return random.choice(candidates) if candidates else (1, 1)
