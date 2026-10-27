"""Figures for the TMLR paper on EES and MLE-bench.

Every figure is built from a file in this package (checksums in SHA256SUMS):

    python make_figures.py            # writes out/fig/*.pdf

Inputs:
  high_eval/eval_results.json               EES High evaluation, three seeds (frozen tag eval-release)
  high_eval/eval_task_metrics.csv           per-run wall time, billed GPU time, tokens
  comparisons/high_per_task_comparison.json   per-task medals for EES, AIBuildAI, MARS+ and Famou-Agent 2.0, with thresholds
  comparisons/mlebench_leaderboard_2026-10-19.md   MLE-bench README leaderboard, read 2026-10-19
"""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
ROOT, FIG = HERE.parent, HERE.parent / "out" / "fig"
FIG.mkdir(parents=True, exist_ok=True)
for f in ("instrument-sans-regular.ttf", "instrument-sans-semibold.ttf"):
    fm.fontManager.addfont(str(HERE / "fonts" / f))

INK, MUTED, LINE, SURFACE = "#0b0b0b", "#52514e", "#e5e5e7", "#fcfcfb"
# Validated categorical pair (dataviz reference palette, slots 1-2): EES / second series.
BLUE, ORANGE = "#2a78d6", "#eb6834"
OTHER = "#b9bec4"
# Medal tiers in medal colours (gold, silver, bronze), checked with the dataviz palette validator
# (all-pairs CVD and normal-vision separation pass; silver is grey by nature). The tier letter in
# every cell is the secondary encoding for print, colour-blind readers and low contrast.
TIER_FILL = {"none": "#f1f3f5", "bronze": "#a8652c", "silver": "#9aa4ae", "gold": "#d4af37"}
TIER_TEXT = {"none": MUTED, "bronze": "white", "silver": INK, "gold": INK}
TIER_LETTER = {"none": "–", "bronze": "B", "silver": "S", "gold": "G"}

plt.rcParams.update({
    "font.family": ["Instrument Sans", "DejaVu Sans"], "font.size": 8.5, "text.color": INK, "axes.labelcolor": MUTED,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.edgecolor": LINE, "axes.linewidth": 0.8,
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.04, "pdf.fonttype": 42,
})

SHORT = {
    "3d-object-detection-for-autonomous-vehicles": "3D detection (lidar)",
    "vinbigdata-chest-xray-abnormalities-detection": "Chest X-ray detection",
    "iwildcam-2019-fgvc6": "Camera traps",
    "predict-volcanic-eruptions-ingv-oe": "Volcanic eruptions",
    "stanford-covid-vaccine": "mRNA degradation",
    "smartphone-decimeter-2022": "Smartphone GNSS",
    "nfl-player-contact-detection": "Player contact",
    "rsna-breast-cancer-detection": "Mammography screening",
    "google-research-identify-contrails-reduce-global-warming": "Contrails",
    "rsna-miccai-brain-tumor-radiogenomic-classification": "Brain-tumour MRI",
    "hms-harmful-brain-activity-classification": "Harmful brain activity",
    "siim-covid19-detection": "COVID-19 chest X-ray",
    "rsna-2022-cervical-spine-fracture-detection": "Cervical-spine fracture",
    "vesuvius-challenge-ink-detection": "Vesuvius ink",
    "bms-molecular-translation": "Molecular translation",
}
DATA_PROPERTY = {"smartphone-decimeter-2022", "hms-harmful-brain-activity-classification"}
NOT_RUN = {"siim-covid19-detection", "rsna-2022-cervical-spine-fracture-detection",
           "vesuvius-challenge-ink-detection", "bms-molecular-translation"}


def clean(ax, grid_axis="x"):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    if grid_axis:
        ax.grid(axis=grid_axis, color=LINE, linewidth=0.8)
    ax.set_axisbelow(True)


def medal_grid(path):
    """Per-task, per-seed medal tier for EES, AIBuildAI, MARS+ and Famou-Agent 2.0 on the 15 High tasks."""
    rows = json.load(open(ROOT / "comparisons" / "high_per_task_comparison.json"))
    count = lambda xs: sum(x != "none" for x in xs)
    rows.sort(key=lambda r: (r["task"] in NOT_RUN, -count(r["ees"]), -count(r["mars"]), SHORT[r["task"]]))
    systems = [("ees", "EES"), ("aibuildai", "AIBuildAI"), ("mars", "MARS+"), ("famou", "Famou-Agent 2.0")]
    cw, ch, gap = 0.36, 0.30, 0.22
    n = len(rows)
    fig, ax = plt.subplots(figsize=(6.8, 0.205 * n + 0.9))
    for i, r in enumerate(rows):
        y = n - 1 - i
        for s, (key, _) in enumerate(systems):
            for k, tier in enumerate(r[key]):
                x = s * (3 * cw + gap) + k * cw
                ax.add_patch(Rectangle((x, y * ch), cw - 0.03, ch - 0.03, facecolor=TIER_FILL[tier],
                                       edgecolor="none"))
                ax.text(x + (cw - 0.03) / 2, y * ch + (ch - 0.03) / 2, TIER_LETTER[tier], ha="center",
                        va="center", fontsize=7, color=TIER_TEXT[tier],
                        fontweight="semibold" if tier != "none" else "normal")
        label = SHORT[r["task"]] + (" \u2020" if r["task"] in DATA_PROPERTY else "")
        label += "  (not run)" if r["task"] in NOT_RUN else ""
        ax.text(-0.12, y * ch + ch / 2 - 0.015, label, ha="right", va="center", fontsize=7.8,
                color=MUTED if r["task"] in NOT_RUN else INK)
    for s, (_, name) in enumerate(systems):
        x0 = s * (3 * cw + gap)
        ax.text(x0 + 1.5 * cw - 0.015, n * ch + 0.16, name, ha="center", va="bottom", fontsize=8.2,
                fontweight="semibold" if s == 0 else "normal", color=INK)
        for k in range(3):
            ax.text(x0 + k * cw + (cw - 0.03) / 2, n * ch + 0.02, str(k + 1), ha="center", va="bottom",
                    fontsize=6.5, color=MUTED)
    width = len(systems) * (3 * cw) + (len(systems) - 1) * gap
    ax.set_xlim(-2.2, width + 0.05)
    ax.set_ylim(-0.05, n * ch + 0.45)
    ax.axis("off")
    fig.savefig(path)
    plt.close(fig)


def _leaderboard():
    rows = []
    for line in open(ROOT / "comparisons" / "mlebench_leaderboard_2026-10-19.md"):
        c = [x.strip() for x in line.split("|")]
        if len(c) < 9 or not c[1] or c[1].startswith("-") or c[1] == "Agent":
            continue
        name = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", c[1]).replace("<br>", " ")
        name = re.sub(r"\s*\(Fractal AI Research\)", "", name)
        llm = re.sub(r"\[\^\d+\]", "", c[2])
        m = re.match(r"([\d.]+)\s*±\s*([\d.]+)", re.sub(r"\[\^\d+\]", "", c[5]))
        rows.append((name, llm, float(m.group(1)), float(m.group(2)), c[7]))
    return rows


def leaderboard(path, top=8):
    """High-split any-medal rate, EES against the strongest main-leaderboard entries."""
    rows = sorted(_leaderboard(), key=lambda r: -r[2])[:top]
    rows = [("EES (this work)", "GPT-6-Luna", 66.67, 0.0, "24", True)] + [r + (False,) for r in rows]
    fig, ax = plt.subplots(figsize=(5.6, 0.27 * len(rows) + 0.5))
    y = list(range(len(rows)))[::-1]
    for yi, (name, llm, v, se, hours, ours) in zip(y, rows):
        ax.barh(yi, v, height=0.62, color=BLUE if ours else OTHER, zorder=2)
        if se > 0:
            ax.errorbar(v, yi, xerr=se, fmt="none", ecolor=INK, elinewidth=0.8, capsize=2, zorder=3)
        ax.text(v + se + 1.2, yi, f"{v:.2f}", va="center", fontsize=8,
                fontweight="semibold" if ours else "normal", color=INK if ours else MUTED)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r[0]}  ·  {r[1]}" + ("" if r[4] == "24" else f"  ·  {r[4]} h") for r in rows],
                       fontsize=7.8)
    for lab, r in zip(ax.get_yticklabels(), rows):
        if r[5]:
            lab.set_fontweight("semibold")
            lab.set_color(INK)
    ax.set_xlim(0, 80)
    ax.set_xticks([0, 20, 40, 60, 80])
    ax.set_xlabel("High split, any-medal rate (%), mean ± s.e. over three seeds")
    clean(ax)
    fig.savefig(path)
    plt.close(fig)


def resources(path):
    """Wall-clock and billed GPU hours per run, three seeds per task."""
    runs = list(csv.DictReader(open(ROOT / "high_eval" / "eval_task_metrics.csv")))
    by = defaultdict(list)
    for r in runs:
        by[r["task"]].append(r)
    order = sorted(by, key=lambda t: -max(float(r["wall_hours"]) for r in by[t]))
    fig, ax = plt.subplots(figsize=(5.6, 0.25 * len(order) + 0.6))
    for i, t in enumerate(order):
        y = len(order) - 1 - i
        walls = [float(r["wall_hours"]) for r in by[t]]
        gpus = [float(r["gpu_hours"]) for r in by[t]]
        ax.plot([min(gpus + walls), max(gpus + walls)], [y, y], color=LINE, linewidth=1, zorder=1)
        ax.scatter(walls, [y + 0.12] * 3, s=16, color=BLUE, edgecolor=SURFACE, linewidth=0.8, zorder=3,
                   label="wall-clock hours" if i == 0 else None)
        ax.scatter(gpus, [y - 0.12] * 3, s=16, color=ORANGE, edgecolor=SURFACE, linewidth=0.8, zorder=3,
                   marker="D", label="billed GPU hours" if i == 0 else None)
    ax.axvline(24, color=MUTED, linewidth=0.9, linestyle=(0, (4, 3)), zorder=1)
    ax.text(23.8, len(order) - 0.45, "24 h limit", ha="right", va="center", fontsize=7.2, color=MUTED)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([SHORT[t] for t in order][::-1], fontsize=7.8)
    ax.set_xlim(-0.5, 25)
    ax.set_xticks([0, 6, 12, 18, 24])
    ax.set_xlabel("hours per run (one marker per seed)")
    clean(ax)
    ax.legend(loc="lower right", frameon=False, fontsize=7.6, handletextpad=0.3)
    fig.savefig(path)
    plt.close(fig)


if __name__ == "__main__":
    medal_grid(FIG / "high_medal_grid.pdf")
    leaderboard(FIG / "high_leaderboard.pdf")
    resources(FIG / "resources.pdf")
    print("wrote", *sorted(p.name for p in FIG.glob("*.pdf")))
