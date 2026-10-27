# Supplementary material: EES on MLE-bench

This package holds the evidence behind the paper's MLE-bench results. It contains every graded submission of the High evaluation, with its grade report, terminal record, launch manifest and decision trace. It also holds the pre-registrations written before any run started, the records of the ablation study, the Lite development ledger, the leaderboard data used for the comparisons, and the scripts that rebuild the paper's tables, figures and statistics from these files. The engine itself is not included.

## How the evaluation was run

We froze one release of the engine and ran it on the 15 competitions of the MLE-bench High split, with three seeds (101, 202, 303). Before the first launch, we wrote a pre-registration that fixed the code, the launch line of every campaign, the budgets, the seeds and the reporting rule. Eleven competitions were launched once per seed, which gives 33 runs. The other four were not launched, and each counts as a miss in every seed. Every run was graded exactly once with OpenAI's MLE-bench grading logic, and no score was read until every run of a seed had finished. One run (seed 101 of the contrails competition) died while downloading its input data, before any training or score. The rule allows one relaunch in that case, and both the cause and the failed first attempt are kept here. `high_eval/protocol.md` describes the procedure in full and quotes the rule.

The result is 10 of 15 competitions with a medal in each of the three seeds (66.67% ± 0.00). Two of these results are labelled as data properties rather than learned models, and the ledger reports them in their own rows. On `smartphone-decimeter-2022`, the answers can be reconstructed from raw files in the public data, a known MLE-bench issue (#93). On `hms-harmful-brain-activity-classification`, the gain over the signal model comes from the layout of the public test index, not from a better model.

## How to verify

From the package root, run:

```
python scripts/verify.py
```

The script checks every file against `SHA256SUMS`. It hashes each of the 33 graded submissions and compares the digest with the ledger, the grade report, the grade claim and receipt, and the terminal record. It confirms that each run was graded once, and it recomputes the count of 10 of 15 per seed from the grade reports alone. It also matches the ledger's campaigns against the pre-registration, checks the 26 ablation records against the ablation tables, recomputes the Lite counts, and runs `scripts/per_task_stats.py`. The checks use only the Python standard library. The statistics script needs numpy.

To re-grade any submission independently, prepare the competition with OpenAI's unmodified MLE-bench and run:

```
mlebench grade-sample high_eval/runs/<competition>/seed-<seed>/submission.csv <competition>
```

The tables and figures of the paper are rebuilt with `python scripts/make_tables.py`, `python scripts/make_ablation.py` and `python scripts/make_figures.py` (the figure script needs matplotlib). Their output goes to `out/`. The rebuilt tables are identical to those in the paper.

## Contents

| Path | What it holds |
|---|---|
| `high_eval/ledger.json` | The 33-run ledger: score, medal, stop reason, flags and submission SHA-256 for every (competition, seed), with medal thresholds and the summary counts |
| `high_eval/protocol.md` | The procedure and the pre-registered rule |
| `high_eval/preregistration/` | The pre-registration, written once before the first launch |
| `high_eval/relaunch/` | The relaunch record for the one infrastructure relaunch |
| `high_eval/canary/` | Canary and preflight stage outputs before the seed-101 launches, and a summary of the eleven canary receipts |
| `high_eval/runs/<competition>/seed-<s>/` | Per run: `submission.csv`, `submission.sha256`, `grade.json` (the MLE-bench grade report), `grade_claim.json`, `grade_receipt.json`, `terminal.json` (stop reason, flags, grading state), `launch.json` (launch manifest), `launch_command.json`, `prior.json`, `input_release.json`, `events.jsonl` (state transitions), `decision_trace.jsonl` and `resources.json` (wall time, billed GPU hours, language-model tokens) |
| `high_eval/eval_results.json`, `eval_task_metrics.csv`, `release_components.json` | The collector's output, per-run resource metrics, and per-run use of the capacity ladder and second stages |
| `ablations/` | Ablation tables, summary, resource usage and run log; the four ablation pre-registrations; the relaunch record; and per run the submission, grade report, terminal record and launch manifest (26 runs, plus the relaunched run's first attempt) |
| `lite/ledger.json` | The Lite development ledger: three confirmation runs per competition, with scores, medals and submission SHA-256 |
| `comparisons/` | Per-task medals of EES and the leaderboard entries on High, the leaderboard's grading reports, the leaderboard table as read on 2026-10-19, and the Lite baseline comparison with its protocol and usage |
| `scripts/` | `verify.py`, the table, ablation and figure scripts, `per_task_stats.py`, and the fonts the figures use |
| `SHA256SUMS` | SHA-256 of every file in the package |
| `ORIGINALS.sha256` | SHA-256 of each record before redaction (see below) |

## Redaction for review

The records were redacted for double-blind review. Storage locations, machine paths, image registry paths, cloud account and project identifiers, service-account names and machine ids are replaced by placeholders such as `<redacted-storage>` and `<redacted-path>`. Image references keep their `sha256` digest. The release tag is written `eval-release`, the ablation tags `ablation-release-a` and `ablation-release-b`, and campaign ids are shortened to match (for example `pairs-eval-release-s101`). Environment-variable and schema names lost their product prefix. Scores, medals, thresholds, timestamps, hashes, code commits and tree digests are unchanged, and the submission files are byte-for-byte the files that were graded. Because redaction changes the bytes of the text records, `ORIGINALS.sha256` lists the SHA-256 of each record as it was before redaction, so the unredacted originals can be checked against this package after review.
