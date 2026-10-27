"""Check the supplementary package against itself.

    python scripts/verify.py            # from the package root (or any directory)

1. Every file listed in SHA256SUMS has that digest.
2. High evaluation: every graded submission hashes to the SHA-256 in the ledger, and the grade
   report, the grade claim and receipt, the terminal record and submission.sha256 all name the
   same digest; each run was graded exactly once; the score and medal in the grade report are
   the ledger's. The any-medal count per seed is recomputed from the grade reports alone.
3. The pre-registration names every campaign in the ledger (the one relaunch through its
   relaunch record), and the ledger's rule is the pre-registered rule.
4. Ablations: each of the 26 records is graded once, its submission matches its grade report,
   and its score and medal are the ablation table's.
5. Lite: the per-run medal counts are recomputed from the Lite ledger.
6. per_task_stats.py is run (it needs numpy) to print the per-task comparison statistics.

Only the standard library is used for checks 1-5. The exit status is non-zero if any check fails.
"""
import hashlib
import json
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEDALS = ("gold", "silver", "bronze")
failures = []


def fail(msg):
    failures.append(msg)
    print("  FAIL", msg)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def check_sums():
    print("[1] SHA256SUMS")
    listed = 0
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        listed += 1
        p = ROOT / name
        if not p.exists():
            fail(f"missing file {name}")
        elif sha256(p) != digest:
            fail(f"digest mismatch {name}")
    print(f"  {listed} files checked")


def run_dir(task, seed):
    return ROOT / "high_eval" / "runs" / task / f"seed-{seed}"


def check_high():
    print("[2] High evaluation, three seeds")
    ledger = load(ROOT / "high_eval" / "ledger.json")
    if ledger.get("schema") != "mlebench-high15-eval:v1":
        fail(f"unexpected ledger schema {ledger.get('schema')}")
    seeds = ledger["seeds"]
    per_seed = {s: 0 for s in seeds}
    matched = total = 0
    for task in ledger["tasks"]:
        if not task["run"]:
            continue  # not launched: a miss for every seed
        for cell in task["seeds"]:
            total += 1
            d = run_dir(task["task_id"], cell["seed"])
            subs = sorted(d.glob("submission.*"))
            subs = [p for p in subs if p.name != "submission.sha256"]
            if len(subs) != 1:
                fail(f"{d}: {len(subs)} submission files")
                continue
            digest = sha256(subs[0])
            grade = load(d / "grade.json")
            claim = load(d / "grade_claim.json")
            receipt = load(d / "grade_receipt.json")
            terminal = load(d / "terminal.json")
            named = {
                "ledger": cell["submission_sha256"],
                "submission.sha256": (d / "submission.sha256").read_text().split()[0],
                "grade": grade.get("submission_sha256"),
                "claim": claim.get("submission_sha256"),
                "receipt": receipt.get("submission_sha256"),
                "terminal": terminal.get("submission_sha256"),
            }
            bad = {k: v for k, v in named.items() if v != digest}
            if bad:
                fail(f"{task['task_id']} seed {cell['seed']}: file {digest[:12]} but {bad}")
            else:
                matched += 1
            if grade.get("grade_count") != 1 or terminal.get("grade_count") != 1:
                fail(f"{task['task_id']} seed {cell['seed']}: graded {grade.get('grade_count')} times")
            medal = (grade.get("grade") or {}).get("any_medal") or None  # "" when no medal
            if grade.get("score") != cell["score"] or medal != cell["medal"]:
                fail(f"{task['task_id']} seed {cell['seed']}: grade {grade.get('score')}/{medal} vs ledger {cell['score']}/{cell['medal']}")
            if medal in MEDALS:
                per_seed[cell["seed"]] += 1
    print(f"  submission SHA-256 matches: {matched}/{total}")
    n = len(ledger["tasks"])
    rates = []
    for s in seeds:
        rate = 100 * per_seed[s] / n
        rates.append(rate)
        claimed = next(p for p in ledger["summary"]["per_seed"] if p["seed"] == s)
        ok = claimed["medal_tasks"] == per_seed[s]
        print(f"  seed {s}: {per_seed[s]}/{n} competitions with a medal ({rate:.2f}%)"
              f"{'' if ok else '  (ledger says ' + str(claimed['medal_tasks']) + ')'}")
        if not ok:
            fail(f"seed {s} count")
    se = statistics.stdev(rates) / len(rates) ** 0.5
    print(f"  any-medal rate: {statistics.mean(rates):.2f} +/- {se:.2f} (mean +/- s.e. over seeds)")
    dp = [t["task_id"] for t in ledger["tasks"] if t.get("data_property")]
    print(f"  labelled data properties: {', '.join(dp)}")
    for s in seeds:
        k = sum(1 for t in ledger["tasks"] if t["run"] and not t.get("data_property")
                for c in t["seeds"] if c["seed"] == s and c["medal"] in MEDALS)
        print(f"  seed {s} without the two data-property rows: {k}/{n - len(dp)} competitions with a medal")
    every = [t["task_id"] for t in ledger["tasks"] if t["run"] and all(c["medal"] in MEDALS for c in t["seeds"])]
    print(f"  medal in every seed: {len(every)} competitions ({len([t for t in every if t not in dp])} without the data-property rows)")
    return ledger


def check_prereg(ledger):
    print("[3] pre-registration and relaunch")
    pre = load(ROOT / "high_eval" / "preregistration" / "preregistration.json")
    relaunches = {}
    for p in (ROOT / "high_eval" / "relaunch").glob("*.json"):
        r = load(p)
        relaunches[r["campaign_id"]] = r
    if pre["rule"] != ledger["rule"]:
        fail("ledger rule differs from the pre-registered rule")
    registered = {}
    for t in pre["tasks"]:
        for seed, c in t["campaigns"].items():
            registered[(t["task"], int(seed))] = c["campaign_id"]
    n = 0
    for task in ledger["tasks"]:
        for cell in task["seeds"]:
            want = registered.get((task["task_id"], cell["seed"]))
            if want in relaunches:
                want = relaunches[want]["relaunch_campaign_id"]
            if want != cell["campaign_id"]:
                fail(f"{task['task_id']} seed {cell['seed']}: ledger {cell['campaign_id']} vs pre-registered {want}")
            n += cell["campaign_id"] is not None
    launched = {t["task"] for t in pre["tasks"]}
    print(f"  {n} ledger runs match the pre-registration ({len(launched)} tasks x {len(pre['seeds'])} seeds); "
          f"{len(relaunches)} recorded relaunch: {', '.join(r['relaunch_campaign_id'] for r in relaunches.values())}")
    first = run_dir("google-research-identify-contrails-reduce-global-warming", 101) / "first_attempt"
    print(f"  relaunched run's first attempt kept: {sorted(p.name for p in first.iterdir())}")


def check_ablations():
    print("[4] ablations")
    A = ROOT / "ablations"
    n = ok = 0
    for f in sorted(A.glob("ablations_*.json")):
        for table in load(f)["tables"]:
            for row in table["rows"]:
                for cell in row["seeds"]:
                    n += 1
                    d = A / "runs" / table["ablation"] / row["task"] / f"seed-{cell['seed']}"
                    sub = [p for p in d.glob("submission.*") if p.name != "submission.sha256"]
                    grade = load(d / "grade.json")
                    terminal = load(d / "terminal.json")
                    digest = sha256(sub[0]) if len(sub) == 1 else None
                    medal = (grade.get("grade") or {}).get("any_medal") or "none"
                    good = (digest is not None and digest == grade.get("submission_sha256") == terminal.get("submission_sha256")
                            and grade.get("grade_count") == 1 and grade.get("score") == cell["score"] and medal == cell["medal"])
                    if good:
                        ok += 1
                    else:
                        fail(f"ablation {table['ablation']} {row['task']} seed {cell['seed']}")
    pre = sorted(p.name for p in (A / "preregistration").glob("*.json"))
    print(f"  {ok}/{n} ablation records consistent; pre-registrations: {', '.join(pre)}")


def check_lite():
    print("[5] Lite three-run ledger")
    d = load(ROOT / "lite" / "ledger.json")
    k = d["summary"]["confirmation_runs"]
    counts = [sum(1 for t in d["tasks"] if t["confirmations"][i]["medal"] in MEDALS) for i in range(k)]
    n = len(d["tasks"])
    print(f"  medal tasks per confirmation run: {', '.join(f'{c}/{n}' for c in counts)}")
    if any(c != d["summary"]["medal_tasks"] for c in counts):
        fail("Lite counts differ from the ledger summary")
    sha_ok = all(len(c["submission_sha256"]) == 64 for t in d["tasks"] for c in t["confirmations"] if c["medal"] in MEDALS)
    print(f"  every medal confirmation names a 64-hex submission SHA-256: {sha_ok}")
    if not sha_ok:
        fail("Lite confirmation without a submission digest")


def run_stats():
    print("[6] per-task comparison statistics (scripts/per_task_stats.py)")
    try:
        import numpy  # noqa: F401
    except ImportError:
        print("  skipped: numpy is not installed")
        return
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "per_task_stats.py")], capture_output=True, text=True)
    print("  " + out.stdout.strip().replace("\n", "\n  "))
    if out.returncode:
        fail("per_task_stats.py failed: " + out.stderr.strip())


if __name__ == "__main__":
    check_sums()
    ledger = check_high()
    check_prereg(ledger)
    check_ablations()
    check_lite()
    run_stats()
    print("OK" if not failures else f"{len(failures)} check(s) failed")
    sys.exit(1 if failures else 0)
