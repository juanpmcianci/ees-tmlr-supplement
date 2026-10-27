"""Appendix tables for the TMLR paper on EES, generated from the package data (checksums in SHA256SUMS).

    python make_tables.py      # writes out/tables/*.tex

Inputs:
  high_eval/eval_task_metrics.csv           per-run score, medal, wall time, billed GPU time, tokens, attempts
  comparisons/high_per_task_comparison.json   medal thresholds per High competition (from the public grading reports)
  lite/ledger.json           the public Lite development ledger
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT, OUT = HERE.parent, HERE.parent / "out" / "tables"

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
END = {"exploration_exhausted": "E", "salvage_finalized": "S", "controller_failure_finalized": "R",
       "no_admissible_route": "N"}
MEDAL = {"gold": "gold", "silver": "silver", "bronze": "bronze", "none": "--", "": "--"}


def tex(s):
    return (str(s).replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("%", "\\%")
            .replace("_", "\\_").replace("#", "\\#").replace("$", "\\$"))


def num(x):
    v = float(x)
    if abs(v) >= 1000:
        return f"{v:,.0f}".replace(",", "{,}")
    return f"{v:.5f}".rstrip("0").rstrip(".") if v else "0"


def runs_table():
    rows = list(csv.DictReader(open(ROOT / "high_eval" / "eval_task_metrics.csv")))
    order = list(SHORT)
    rows.sort(key=lambda r: (order.index(r["task"]), int(r["seed"])))
    lines = []
    prev = None
    for r in rows:
        name = tex(SHORT[r["task"]]) + ("$^\\dagger$" if r["task"] in DATA_PROPERTY else "")
        flags = [END.get(r["stop_reason"], "?")]
        if r["relaunched"] == "True":
            flags.append("L")
        tokens = (float(r["llm_input_tokens"]) + float(r["llm_output_tokens"])) / 1e6
        if prev is not None and prev != r["task"]:
            lines.append("\\addlinespace[2pt]")
        lines.append(" & ".join([
            name if prev != r["task"] else "", r["seed"], num(r["score"]), MEDAL[r["medal"]],
            f"{float(r['wall_hours']):.1f}", f"{float(r['gpu_hours']):.1f}", f"{tokens:.2f}", r["attempts"],
            "/".join(flags),
        ]) + " \\\\")
        prev = r["task"]
    (OUT / "runs.tex").write_text("\n".join(lines) + "\n")


def thresholds_table():
    rows = json.load(open(ROOT / "comparisons" / "high_per_task_comparison.json"))
    order = list(SHORT)
    rows.sort(key=lambda r: order.index(r["task"]))
    lines = []
    for r in rows:
        lines.append(" & ".join([
            tex(SHORT[r["task"]]), "lower" if r["lower"] else "higher",
            num(r["bronze"]), num(r["silver"]), num(r["gold"]),
        ]) + " \\\\")
    (OUT / "thresholds.tex").write_text("\n".join(lines) + "\n")


def lite_table():
    d = json.load(open(ROOT / "lite" / "ledger.json"))
    lines = []
    for t in sorted(d["tasks"], key=lambda t: t["task_id"]):
        conf = [MEDAL[c["medal"] or ""] for c in t["confirmations"]]
        lines.append(" & ".join([
            tex(t["task_id"]), MEDAL[t["best_medal"] or ""], *conf, tex(t["method"]),
        ]) + " \\\\")
    (OUT / "lite.tex").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    runs_table()
    thresholds_table()
    lite_table()
    print("wrote", *sorted(p.name for p in OUT.glob("*.tex")))
