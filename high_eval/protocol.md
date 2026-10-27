# How the High evaluation was run

This note describes the procedure behind every record in `high_eval/`. The rule quoted below is the one written into the pre-registration (`preregistration/preregistration.json`) before the first campaign started. The ledger (`ledger.json`) repeats it word for word, and `scripts/verify.py` checks that the two agree.

## What was evaluated

One frozen release of the engine, called `eval-release` in this package. It is identified by its code commit `926abe7d0c17c767b564ee303fb7924b412f2133` and by the SHA-256 digest of its deployed source tree, `6ca8ec9aa2c40bf27d36dd45d8bb9f66c71548529431ee8de66b4265fe92fe36`. Each machine refused to start a campaign from any other tree. The release used one language model, GPT-6-Luna, and a method-only prior: strategy notes with no rated outcomes. The prior's manifest digest, `87036fb4…`, is recorded in every terminal record.

The benchmark is the 15-competition High split of MLE-bench. Eleven competitions were launched. Four were not launched (`siim-covid19-detection`, `rsna-2022-cervical-spine-fracture-detection`, `vesuvius-challenge-ink-detection`, `bms-molecular-translation`) and count as a miss in every seed. The denominator is 15 for every seed.

Three seeds were used: 101, 202 and 303. Each (competition, seed) pair was launched once, which gives 33 runs. The time limit was 24 hours per run. The engine's own budget for each competition was fixed in the pre-registration (`budget_seconds`, between 1.5 and 23 hours).

## Order of operations

1. **Freeze and deploy.** The release was cut from an annotated tag and deployed as a source tree whose digest is checked on every machine.
2. **Canary.** For each launched competition, one data-bound shape canary ran from the frozen tree on a small fixture that has the competition's data shape. A passing canary writes a receipt bound to the code commit and to the exact launch data (object URI and version id). A receipt authorises launches for 72 hours, and the launcher refuses to start a campaign without a valid one. `canary/` holds the canary and preflight stage outputs that came before the seed-101 launches, together with a parsed summary of the eleven receipts.
3. **Preflight.** On each machine, every launch check runs without starting anything: scoring assets, sandbox, disk space against the competition's measured peak, cores, the canary receipt, prior, answers pin and model weights.
4. **Pre-registration.** Before the first launch, a pre-registration file was written to the campaign store with a create-once write. It records the tag, the tree digest, the launch-line digest of every campaign, the prior, budgets, instance maps, the seeds and the rule. A later invocation for another seed has to reproduce the same bytes or it stops.
5. **Launch.** Each campaign ran hands-off, with no environment overrides, under a campaign id of the form `<row>-eval-release-s<seed>`.
6. **Grading.** Each run was graded once with OpenAI's MLE-bench grading logic. A claim record (`grade_claim.json`) is written before grading. The outcome (`grade.json`) and receipt (`grade_receipt.json`) are written after it. All three name the SHA-256 of the graded submission.
7. **Collection.** No score was read until every campaign of a seed was terminal. The collector checks every terminal record against the pre-registration (tag, commit, tree digest, launch-line digest, prior) before it enters the ledger.

## The rule (verbatim from the pre-registration)

> Three seeds per task, launched once each from the frozen tag; every one of them is reported, whatever it scores, and a task that ends without a score counts as a miss for that seed. No relaunch after a score exists. A campaign that died of an infrastructure cause (capacity, quota, disk, credentials, a cloud outage) before any score was taken may be relaunched once, under a new campaign id, with the cause recorded before the relaunch; the first attempt's evidence is kept. Nothing is salvaged, re-finalised or scored by hand. No score is read before every campaign of the seed is terminal. Results labelled as a data property are reported in their own row and are not added to the model-driven count.

## Flags on individual runs

- **relaunched**: the first attempt died of an infrastructure cause before any score existed, and it was relaunched once under the rule, with the cause recorded before the relaunch.
- **salvage**: the run ended without a handed-over deliverable. The engine controller's built-in terminal salvage finalised the run's best verified attempt by its recorded validation score, with no held-out signal, before the single grade. This is part of the frozen engine. Nobody intervened by hand.
- **recovery**: the controller failed before its handoff. The engine's built-in recovery finalised the deliverable from the run's own reviewed attempts before the single grade.

## The one relaunch

Seed 101 of `google-research-identify-contrails-reduce-global-warming` died at 2026-10-13T17:44Z while downloading its 323 GB public input archive. The storage response stream broke after 314 of 323 GB, before any training or score. The cause was recorded at 2026-10-14T21:03Z (`relaunch/bandseg-eval-release-s101.json`), and the relaunch `bandseg-eval-release-s101-relaunch1` started after that. The first attempt never reached a terminal state, so it has no terminal record (`first_terminal` is `null` in the relaunch record). Its launch manifest, launch command, prior record and last checkpoint index are kept in `runs/google-research-identify-contrails-reduce-global-warming/seed-101/first_attempt/`.

## Two results labelled as data properties

Two competitions earn medals for reasons that have nothing to do with learning, and the ledger labels them in their own rows.

- `smartphone-decimeter-2022`: the answers can be reconstructed from raw files shipped with the public data. This is a known MLE-bench issue (#93). The score is 0.0 in every seed, and the three submissions are byte-identical.
- `hms-harmful-brain-activity-classification`: the gain over the signal model comes from the layout of the public test index (rows per recording, order, length), not from a better model.

## Ablations

The four ablations follow the same procedure. Each has its own pre-registration (`ablations/preregistration/`), launched from its own tag (`ablation-release-a` at commit `d492c11920c4`, or `ablation-release-b` at commit `ba3f8cc66be0`). Each pre-registration names the release it is compared against and states, in its field `differs_from_release_by`, the launch argument that switches the component off. Their rule, also quoted verbatim from those files, uses two seeds (101 and 202) per (ablation, competition) cell. It reports every run beside the release run of the same seed and never adds an ablation result to the release count. It also flags a cell as capacity-affected when the ablated run received less than half of the release run's billed GPU hours. That gives 26 runs. One of them (`imgdet-abl-no-llm-reasoning-ablation-release-a-s101`) was relaunched after an input-download failure before any score. Its relaunch record is in `ablations/relaunch/`.
