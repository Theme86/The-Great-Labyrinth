# stats_collector.py  –  The Great Labyrinth
import csv
import os

COMBAT_FIELDS = ["run_id", "floor", "killed", "dmg_taken", "dmg_dealt", "potions"]
SHOP_FIELDS   = ["run_id", "floor", "money_spent"]

class StatsCollector:
    def __init__(self):
        self.combat_log = []
        self.shop_log   = []
        self.run_id     = self._load_last_run_id()
        self._enc       = self._blank_enc()
        self._saved     = False

    @staticmethod
    def _blank_enc():
        return {"killed": 0, "dmg_taken": 0, "dmg_dealt": 0, "potions": 0}

    def reset_run(self):
        self.combat_log.clear()
        self.shop_log.clear()
        self.run_id += 1
        self._enc   = self._blank_enc()
        self._saved = False

    def add_kill(self):           self._enc["killed"]    += 1
    def add_dmg_taken(self, v):   self._enc["dmg_taken"] += v
    def add_dmg_dealt(self, v):   self._enc["dmg_dealt"] += v
    def add_potion(self):         self._enc["potions"]   += 1

    def record_encounter(self, floor):
        self.combat_log.append({"run_id": self.run_id, "floor": floor, **self._enc})
        self._enc   = self._blank_enc()
        self._saved = False

    def record_shop(self, floor, spent):
        self.shop_log.append({"run_id": self.run_id, "floor": floor, "money_spent": spent})
        self._saved = False

    def save_to_csv(self):
        if self._saved:
            return
        self._saved = True
        for fname, data, fields in [
            ("combat_log.csv", self.combat_log, COMBAT_FIELDS),
            ("shop_log.csv",   self.shop_log,   SHOP_FIELDS),
        ]:
            if not data:
                continue
            file_is_new = (not os.path.exists(fname)) or os.path.getsize(fname) == 0
            with open(fname, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
                if file_is_new:
                    w.writeheader()
                w.writerows(data)
        print("Saved combat_log.csv & shop_log.csv")

    def get_summary(self):
        if not self.combat_log:
            return {}
        return {
            "enemies_killed": sum(r["killed"]    for r in self.combat_log),
            "damage_taken":   sum(r["dmg_taken"] for r in self.combat_log),
            "damage_dealt":   sum(r["dmg_dealt"] for r in self.combat_log),
            "potions_used":   sum(r["potions"]   for r in self.combat_log),
        }

    def _load_last_run_id(self):
        try:
            with open("combat_log.csv", "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
                return int(rows[-1]["run_id"]) + 1 if rows else 1
        except (FileNotFoundError, KeyError, ValueError):
            return 1


