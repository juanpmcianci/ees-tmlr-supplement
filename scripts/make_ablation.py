"""Ablation table (Table 5) for the TMLR paper on EES, generated from the package data.

    python make_ablation.py      # writes out/tables/ablations.tex and out/ablation_summary.json

Inputs:
  ablations/ablations_ablation-release-a.json    `bench.eval_kit.collect --ablation all` for tag ablation-release-a
  ablations/ablations_ablation-release-b.json   the same for tag ablation-release-b
  high_eval/eval_results.json              the release's collected results (seeds 101, 202, 303)
  high_eval/eval_task_metrics.csv          the release's per-run wall and billed GPU hours
  ablations/ablation_usage.json            per ablated campaign: wall and billed GPU hours, unbilled jobs
  comparisons/high_per_task_comparison.json  medal thresholds and metric direction

Each ablated seed is compared with the release run of the same seed. The change column is the
relative change of the two-seed mean score, signed so that a positive value is an improvement.
The capacity clause of the pre-registered rule is applied here: a cell whose ablated run received
less than half of the release run's billed GPU hours is flagged as capacity-affected.
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT, OUT = HERE.parent, HERE.parent / "out" / "tables"

CONDITION = {
    "no_llm_reasoning": "No language model",
    "no_capacity_ladder": "No capacity ladder",
    "no_second_stages": "No second stages",
    "no_method_prior": "No method prior",
}
ROW_ORDER = ("seqgraph", "longtail", "cohort", "segments", "pairs", "detection", "signal")
SHORT = {
    "seqgraph": "mRNA degradation", "longtail": "Camera traps", "cohort": "Brain-tumour MRI",
    "segments": "Volcanic eruptions", "pairs": "Player contact", "detection": "Chest X-ray detection",
    "signal": "Harmful brain activity",
}
LETTER = {"gold": "G", "silver": "S", "bronze": "B", "none": "--", None: "?"}
SEEDS = (101, 202)


def fmt(score, task):
    if task == "predict-volcanic-eruptions-ingv-oe":
        return f"{score / 1e6:.3f}"
    return f"{score:.4f}"


def main():
    release = {r["name"]: r for r in json.load(open(ROOT / "high_eval" / "eval_results.json"))["rows"]}
    rel_gpu = {(r["row"], int(r["seed"])): float(r["gpu_hours"])
               for r in csv.DictReader(open(ROOT / "high_eval" / "eval_task_metrics.csv"))}
    rel_wall = {(r["row"], int(r["seed"])): float(r["wall_hours"])
                for r in csv.DictReader(open(ROOT / "high_eval" / "eval_task_metrics.csv"))}
    usage = json.load(open(ROOT / "ablations" / "ablation_usage.json"))["campaigns"]
    thresholds = {r["task"]: r for r in json.load(open(ROOT / "comparisons" / "high_per_task_comparison.json"))}
    tables = []
    for f in ("ablations_ablation-release-a.json", "ablations_ablation-release-b.json"):
        tables += json.load(open(ROOT / "ablations" / f))["tables"]

    summary, lines = [], []
    for table in sorted(tables, key=lambda t: list(CONDITION).index(t["ablation"])):
        assert not table["refused"], table["refused"]
        rows = sorted(table["rows"], key=lambda r: ROW_ORDER.index(r["name"]))
        for i, row in enumerate(rows):
            task, name = row["task"], row["name"]
            lower = thresholds[task]["lower"]
            rel_cells = {c["seed"]: c for c in release[name]["seeds"]}
            rel = [rel_cells[s] for s in SEEDS]
            abl = {c["seed"]: c for c in row["seeds"]}
            abl = [abl[s] for s in SEEDS]
            rel_mean = sum(c["score"] for c in rel) / 2
            abl_mean = sum(c["score"] for c in abl) / 2
            change = (abl_mean - rel_mean) / abs(rel_mean) * (-1 if lower else 1)
            rel_scores3 = [c["score"] for c in release[name]["seeds"]]
            spread3 = (max(rel_scores3) - min(rel_scores3)) / abs(sum(rel_scores3) / 3)
            gpu_abl = [usage[c["campaign_id"]]["gpu_hours"] for c in abl]
            gpu_rel = [rel_gpu[(name, s)] for s in SEEDS]
            affected = [g < 0.5 * r for g, r in zip(gpu_abl, gpu_rel) if r > 0]
            rec = {
                "ablation": table["ablation"], "tag": table["tag"], "row": name, "task": task,
                "lower_is_better": lower,
                "release": [{"seed": c["seed"], "score": c["score"], "medal": c["medal"]} for c in rel],
                "ablated": [{"seed": c["seed"], "score": c["score"], "medal": c["medal"],
                             "campaign_id": c["campaign_id"], "relaunched": c["relaunched"],
                             "stop_reason": c.get("stop_reason"), "counts": c.get("ablation_counts")}
                            for c in abl],
                "release_medal_seed_runs": sum(c["medal"] in ("gold", "silver", "bronze") for c in rel),
                "ablated_medal_seed_runs": row["any_medal_count"],
                "relative_change_of_mean_positive_is_better": round(change, 5),
                "release_three_seed_relative_range": round(spread3, 5),
                "gpu_hours_ablated": gpu_abl, "gpu_hours_release": gpu_rel,
                "unbilled_jobs_ablated": [usage[c["campaign_id"]]["unbilled_jobs"] for c in abl],
                "wall_hours_ablated": [usage[c["campaign_id"]]["wall_hours"] for c in abl],
                "wall_hours_release": [rel_wall[(name, s)] for s in SEEDS],
                "capacity_affected": any(affected),
                "flags": row["flags"],
            }
            summary.append(rec)

            def cell(c):
                return f"{fmt(c['score'], task)}\\,{LETTER[c['medal']]}"

            mark = "$^\\dagger$" if "data_property" in row["flags"] else ""
            gpu = ("CPU" if sum(gpu_rel) == 0 else
                   f"{sum(gpu_abl):.1f} / {sum(gpu_rel):.1f}" + ("$^\\ast$" if any(affected) else ""))
            if i == 0:
                lines.append(f"\\multicolumn{{8}}{{@{{}}l}}{{\\emph{{{CONDITION[table['ablation']]}}}}} \\\\")
            lines.append(" & ".join([
                "\\quad " + SHORT[name] + mark,
                cell(rel[0]), cell(rel[1]), cell(abl[0]), cell(abl[1]),
                f"{rec['release_medal_seed_runs']}$\\to${rec['ablated_medal_seed_runs']}",
                f"{change * 100:+.1f}\\%".replace("-", "$-$"),
                gpu,
            ]) + " \\\\")
        lines.append("\\addlinespace[3pt]")
    lines.pop()
    (OUT / "ablations.tex").write_text("\n".join(lines) + "\n")
    totals = {
        cond: {
            "cells": sum(1 for r in summary if r["ablation"] == cond),
            "release_medal_seed_runs": sum(r["release_medal_seed_runs"] for r in summary if r["ablation"] == cond),
            "ablated_medal_seed_runs": sum(r["ablated_medal_seed_runs"] for r in summary if r["ablation"] == cond),
            "capacity_affected_cells": [r["row"] for r in summary if r["ablation"] == cond and r["capacity_affected"]],
        } for cond in CONDITION
    }
    json.dump({"cells": summary, "totals": totals}, open(OUT.parent / "ablation_summary.json", "w"), indent=1)
    for cond, t in totals.items():
        print(cond, t)
    for r in summary:
        print(f"{r['ablation']:19s} {r['row']:9s} medals {r['release_medal_seed_runs']}->{r['ablated_medal_seed_runs']} "
              f"change {r['relative_change_of_mean_positive_is_better'] * 100:+6.2f}%  "
              f"release 3-seed range {r['release_three_seed_relative_range'] * 100:5.2f}%  "
              f"gpu {r['gpu_hours_ablated']} vs {r['gpu_hours_release']}  unbilled {r['unbilled_jobs_ablated']}  "
              f"wall {r['wall_hours_ablated']} vs {r['wall_hours_release']}")


if __name__ == "__main__":
    main()
