# stats_collector.py  –  The Great Labyrinth
# Collects per-encounter and per-shop-visit data; exports to CSV.

import csv
from datetime import datetime


class StatsCollector:
    def __init__(self):
        self.combat_log = []
        self.shop_log   = []
        self.run_id     = self._load_last_run_id()
        self._enc       = self._blank_enc()

    # ── Internal helpers ──────────────────────────────────────────────────────
    @staticmethod
    def _blank_enc():
        return {"killed": 0, "dmg_taken": 0, "dmg_dealt": 0, "potions": 0}

    def reset_run(self):
        self.combat_log.clear()
        self.shop_log.clear()
        self.run_id += 1 
        self._enc = self._blank_enc()

    # ── Per-frame accumulators ────────────────────────────────────────────────
    def add_kill(self):           self._enc["killed"]    += 1
    def add_dmg_taken(self, v):   self._enc["dmg_taken"] += v
    def add_dmg_dealt(self, v):   self._enc["dmg_dealt"] += v
    def add_potion(self):         self._enc["potions"]   += 1

    # ── End-of-floor / end-of-shop recording ─────────────────────────────────
    def record_encounter(self, floor):
        self.combat_log.append({
            "run_id":    self.run_id,
            "floor":     floor,
            "timestamp": datetime.now().isoformat(),
            **self._enc,
        })
        self._enc = self._blank_enc()

    def record_shop(self, floor, spent):
        self.shop_log.append({
            "run_id":      self.run_id,
            "floor":       floor,
            "timestamp":   datetime.now().isoformat(),
            "money_spent": spent,
        })

    # ── Export ────────────────────────────────────────────────────────────────
    def save_to_csv(self):
        for fname, data in [
            ("combat_log.csv", self.combat_log),
            ("shop_log.csv",   self.shop_log),
        ]:
            if not data:
                continue
            with open(fname, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=data[0].keys())
                w.writeheader()
                w.writerows(data)
        print("Saved combat_log.csv & shop_log.csv")

    def get_summary(self):
        if not self.combat_log:
            return {}
        total_killed = sum(r["killed"]    for r in self.combat_log)
        total_dmg_in = sum(r["dmg_taken"] for r in self.combat_log)
        total_dmg_out= sum(r["dmg_dealt"] for r in self.combat_log)
        total_pots   = sum(r["potions"]   for r in self.combat_log)
        return {
            "enemies_killed": total_killed,
            "damage_taken":   total_dmg_in,
            "damage_dealt":   total_dmg_out,
            "potions_used":   total_pots,
        }
    
    def _load_last_run_id(self):
        try:
            with open("combat_log.csv", "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
                return int(rows[-1]["run_id"]) + 1 if rows else 1
        except FileNotFoundError:
            return 1

