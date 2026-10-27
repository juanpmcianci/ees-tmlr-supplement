"""Per-task comparison statistics behind Section 7.2: EES against each leaderboard entry on the 15 High competitions.

Per-task medal rate = fraction of the three seeds that medal. Reports the discordant tasks, an exact two-sided sign test,
and a percentile bootstrap over tasks (20,000 resamples) of the mean per-task difference in medal rate.
"""
import json
from math import comb
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA_PROPERTY = {"smartphone-decimeter-2022", "hms-harmful-brain-activity-classification"}


def rate(tiers):
    return sum(t != "none" for t in tiers) / len(tiers)


def sign_test(wins, n):
    k = max(wins, n - wins)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k, n + 1)) / 2**n) if n else 1.0


def main():
    rows = json.load(open(ROOT / "comparisons" / "high_per_task_comparison.json"))
    rng = np.random.default_rng(20261013)
    for key, name in (("aibuildai", "AIBuildAI"), ("mars", "MARS+"), ("famou", "Famou-Agent 2.0")):
        d = np.array([rate(r["ees"]) - rate(r[key]) for r in rows])
        disc = d[d != 0]
        boots = d[rng.integers(0, len(d), size=(20000, len(d)))].mean(axis=1)
        lo, hi = np.percentile(boots, [2.5, 97.5])
        keep = [r for r in rows if r["task"] not in DATA_PROPERTY]
        d2 = np.array([rate(r["ees"]) - rate(r[key]) for r in keep])
        print(f"{name:16s} discordant {len(disc)} (EES ahead {int((disc > 0).sum())}), two-sided sign p={sign_test(int((disc > 0).sum()), len(disc)):.4f}, "
              f"mean diff {100 * d.mean():.1f} pp [{100 * lo:.1f}, {100 * hi:.1f}]; without data-property tasks: "
              f"{int((d2 != 0).sum())} discordant, EES ahead {int((d2 > 0).sum())}")


if __name__ == "__main__":
    main()
