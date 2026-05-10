# dataanalysis.py  –  The Great Labyrinth
# Reads combat_log.csv and shop_log.csv then shows 5 charts.

import csv
import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ── Load data ─────────────────────────────────────────────────────────────────
def load_csv(fname):
    if not os.path.exists(fname) or os.path.getsize(fname) == 0:
        return []
    with open(fname, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

combat = load_csv("combat_log.csv")
shop   = load_csv("shop_log.csv")

if not combat:
    print("No combat_log.csv found. Play at least one run first.")
    exit()

# ── Parse ─────────────────────────────────────────────────────────────────────
killed   = [int(r["killed"])    for r in combat]
dmg_tkn  = [int(r["dmg_taken"]) for r in combat]
dmg_dlt  = [int(r["dmg_dealt"]) for r in combat]
potions  = [int(r["potions"])   for r in combat]
floors_c = [int(r["floor"])     for r in combat]

money_spent = [int(r["money_spent"]) for r in shop] if shop else []
floors_s    = [int(r["floor"])       for r in shop] if shop else []

# ── Style ─────────────────────────────────────────────────────────────────────
plt.style.use("dark_background")
ACCENT  = "#64d2ff"
RED     = "#e05050"
GOLD    = "#ffd23f"
GREEN   = "#50e08c"
PURPLE  = "#b450ff"
FIG_BG  = "#12090e"
AX_BG   = "#1a1228"

fig = plt.figure(figsize=(18, 11), facecolor=FIG_BG)
fig.suptitle("The Great Labyrinth — Run Statistics", fontsize=18,
             color=ACCENT, fontweight="bold", y=0.98)

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

def style_ax(ax, title):
    ax.set_facecolor(AX_BG)
    ax.set_title(title, color=ACCENT, fontsize=11, pad=8)
    ax.tick_params(colors="gray")
    for sp in ax.spines.values():
        sp.set_color("#332244")

# ── 1. Histogram — enemies killed per encounter ───────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
style_ax(ax1, "1. Enemies Killed per Encounter")
ax1.hist(killed, bins=range(min(killed), max(killed)+2) if killed else 10,
         color=RED, edgecolor="#220011", alpha=0.85)
ax1.set_xlabel("Enemies Killed", color="gray")
ax1.set_ylabel("Frequency", color="gray")

# ── 2. Bar chart — avg money spent per shop visit (by floor) ──────────────────
ax2 = fig.add_subplot(gs[0, 1])
style_ax(ax2, "2. Avg Money Spent per Shop Floor")
if money_spent:
    floor_totals: dict = {}
    floor_counts: dict = {}
    for f, m in zip(floors_s, money_spent):
        floor_totals[f] = floor_totals.get(f, 0) + m
        floor_counts[f] = floor_counts.get(f, 0) + 1
    fl_sorted = sorted(floor_totals)
    avgs = [floor_totals[f] / floor_counts[f] for f in fl_sorted]
    ax2.bar([str(f) for f in fl_sorted], avgs, color=GOLD, edgecolor="#221100", alpha=0.85)
    ax2.set_xlabel("Floor", color="gray")
    ax2.set_ylabel("Avg Gold Spent", color="gray")
else:
    ax2.text(0.5, 0.5, "No shop data yet", ha="center", va="center",
             color="gray", transform=ax2.transAxes)

# ── 3. Box plot — damage taken per encounter ──────────────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
style_ax(ax3, "3. Damage Taken per Encounter")
bp = ax3.boxplot(dmg_tkn, patch_artist=True,
                 medianprops=dict(color=GOLD, linewidth=2),
                 whiskerprops=dict(color="gray"),
                 capprops=dict(color="gray"),
                 flierprops=dict(marker="o", color=RED, markersize=4))
for patch in bp["boxes"]:
    patch.set_facecolor(RED)
    patch.set_alpha(0.6)
ax3.set_ylabel("Damage Taken", color="gray")
ax3.set_xticks([])

# ── 4. Scatter plot — damage dealt vs damage taken ────────────────────────────
ax4 = fig.add_subplot(gs[1, 0:2])
style_ax(ax4, "4. Damage Dealt vs Damage Taken  (each dot = one floor)")
sc = ax4.scatter(dmg_dlt, dmg_tkn,
                 c=floors_c, cmap="plasma",
                 alpha=0.75, edgecolors="none", s=60)
cb = fig.colorbar(sc, ax=ax4)
cb.set_label("Floor", color="gray")
cb.ax.yaxis.set_tick_params(color="gray")
plt.setp(plt.getp(cb.ax.axes, "yticklabels"), color="gray")
ax4.set_xlabel("Damage Dealt", color="gray")
ax4.set_ylabel("Damage Taken", color="gray")
# reference line y=x  (equal trade)
mx = max(max(dmg_dlt, default=1), max(dmg_tkn, default=1))
ax4.plot([0, mx], [0, mx], color="#444466", linestyle="--", linewidth=1, label="1:1 line")
ax4.legend(labelcolor="gray", facecolor=AX_BG, edgecolor="#332244")

# ── 5. Line chart — potions used over encounters ──────────────────────────────
ax5 = fig.add_subplot(gs[1, 2])
style_ax(ax5, "5. Potions Used Over Time")
ax5.plot(range(1, len(potions)+1), potions,
         color=GREEN, linewidth=1.8, marker="o", markersize=4, alpha=0.85)
ax5.fill_between(range(1, len(potions)+1), potions,
                 color=GREEN, alpha=0.15)
ax5.set_xlabel("Encounter #", color="gray")
ax5.set_ylabel("Potions Used", color="gray")
ax5.yaxis.get_major_locator().set_params(integer=True)

plt.savefig("visualization.png", dpi=120, bbox_inches="tight", facecolor=FIG_BG)
print("Saved visualization.png")
plt.show()
