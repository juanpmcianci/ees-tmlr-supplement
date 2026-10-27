# Ablation run log (tag `ablation-release-a`)

Component ablations of the release `eval-release` (`926abe7d0c17`). Plan:
`bench/experiments/ablations/PLAN.md` on branch `<redacted-branch>` (commit `d492c1192`,
annotated tag `ablation-release-a`, pushed). 32 campaigns, seeds 101 and 202. Results feed Table 5 and
Section 6.5 of the paper. No score is read before every campaign of an ablation is terminal.

## Setup (2026-10-20 UTC)

| time (UTC) | event |
|---|---|
| ~02:45 | staging machines `<redacted-instance>`, `<redacted-instance>` started (were stopped); 480 GB / 1,173 GB free on /data |
| ~02:46 | tagged tree deployed to both: code `d492c11920c4`, clean, tree `341acbfc…` |
| 02:47-04:10 | canaries: 7/7 passed (pairs 31 s, segments 17 s, cohort 414 s, seqgraph 978 s, longtail 1045 s, detection 2497 s with two failed g5.4xlarge jobs, signal ~80 min after several unplaced L40S attempts). Receipts valid 72 h, i.e. until about 2026-10-23 02:48-04:10 UTC |
| ~04:15 | preflight: all four ablations, 16 row checks, 0 failures |
| 04:20-12:23 | first launch attempt failed at the first AWS call (SSO token expired while waiting for the go-ahead); verified nothing written |
| 12:26 | **wave 1 launched**; pre-registrations created: `eval-preregistration/ablation-release-a/ablations/no_llm_reasoning/preregistration.json`, `.../no_capacity_ladder/preregistration.json` |

Wave 1 campaigns (seed 101): `longtail-`, `seqgraph-`, `imgvol-`, `imgdet-abl-no-llm-reasoning-ablation-release-a-s101`;
`pairs-`, `segments-abl-no-capacity-ladder-ablation-release-a-s101`.

## 2026-10-20, continued

| time (UTC) | event |
|---|---|
| 12:42 | `imgdet-abl-no-llm-reasoning-ablation-release-a-s101` died 16 min in, downloading its 127 GB input archive (S3 stream broke: IncompleteRead after 92,265,650,203 of 127,407,691,051 bytes), before any training or score |
| 13:16 | relaunched once under the pre-registered rule as `...-s101-relaunch1`; cause recorded create-once at `eval-preregistration/ablation-release-a/relaunches/imgdet-abl-no-llm-reasoning-ablation-release-a-s101.json` |
| 13:1x | second tag `ablation-release-b` (commit `ba3f8cc66`, branch `<redacted-branch>`, pushed) for the two ablations not yet pre-registered: `no_method_prior` trimmed to seqgraph, longtail, segments; `no_second_stages` pairs placed on staging2 cores 0-9. Deployed to both machines (tree `cdfaed4e…`, own code dir); tag-A code dir untouched |
| 13:17 | tag-B canaries started (5 rows); pairs (staging2) and segments passed |
| 13:21 | `pairs-abl-no-second-stages-ablation-release-b-s101` launched on staging2 0-9; pre-registration `eval-preregistration/ablation-release-b/ablations/no_second_stages/preregistration.json` created |
| 13:2x | on-machine launch queues installed (timer off until all tag-B receipts exist): staging 14 queued, staging2 5 queued; dependencies by machine and core set, plus the serialized L40S type (detection and signal alternate). Twice-daily laptop check-in removed |

| 13:35 | tag-B canaries 5/5 passed (code `ba3f8cc66be0`); preflight for no_method_prior (3 rows) and signal: 0 failures |
| 13:3x | pre-registration `eval-preregistration/ablation-release-b/ablations/no_method_prior/preregistration.json` created with the kit's create-once write, the exact bytes the queued launch scripts embed (sha256 `82583e33…`). All four ablations are now pre-registered |
| 13:37 | both queue timers enabled (every 5 min); first run: 14 + 5 waiting, nothing ready yet. Status check scheduled twice a day (about 08:43 and 20:43 local) plus a one-off check after the first expected queue launch |

Expected finish (upper bound, full budgets): Thu 2026-10-22 about 15:30 UTC.

## Dispatch

Superseded at 13:2x: launches are made by the on-machine queues (`<redacted-path>/ablq` on each staging
machine, systemd timer every 5 minutes), which run each campaign's sealed kit-generated launch script once,
when all its predecessors have a terminal record. A failed launch is never retried by the queue.

| check-in (UTC) | terminal / running / not started | launched |
|---|---|---|
| 2026-10-20 12:30 | 0 / 6 / 26 | wave 1 (6) |
| 2026-10-20 13:40 | 0 / 7 / 19 (of 26) | relaunch of detection s101; no_second_stages pairs s101; queues on |
| 2026-10-20 15:10 | 2 / 7 / 17 (of 26) | One-off queue check. Terminal: cohort no_llm s101 and seqgraph no_llm s101 (both ended early). Queue launch of seqgraph no_method_prior s101 at 14:03 was refused by the launch gate (custom_code: `runuser` not found: the queue's systemd PATH lacked /usr/sbin); no campaign folder or S3 object was created. PATH fixed on both machines at 15:09; refusal cleared; seqgraph no_method_prior s101 launched 15:09:39 and cohort no_llm s202 launched 15:10:30, both by the queues |
| 2026-10-21 01:50 | 15 / 4 / 7 (of 26) | Status check: no attention needed; all queue launches in dependency order (detection s101 relaunch terminal, signal s101 launched 00:32, pairs no_llm s101 launched 01:15, pairs no_second_stages s202 launched 01:37). Fixed the status script's own terminal check (a 1,000-key listing missed terminal.json in large campaigns; now an exact lookup) |
| 2026-10-21 13:45 | 18 / 4 / 4 (of 26) | Status check: no attention needed. Queue launches since last check: segments no_capacity_ladder s202 (06:46), detection no_llm s202 (12:41, after signal s101), segments no_llm s202 (12:52). Expected finish about Thu 2026-10-22 15:00 UTC (last: pairs no_llm s202) |
| 2026-10-21 22:46 | 21 / 3 / 2 (of 26) | On-request status: no attention needed. Queue launches since last check: pairs no_capacity_ladder s202 (13:46), segments no_method_prior s202 (18:57). Remaining: pairs no_llm s202 (after pairs no_capacity s202, ~02:15) and signal s202 (after detection s202, ~01:10); expected finish about Thu 2026-10-22 14:45 UTC |
| 2026-10-22 13:13 | 25 / 1 / 0 (of 26) | Status on request: queue launched signal no_second_stages s202 (00:51) and pairs no_llm s202 (02:29); everything else terminal. staging2 idle (0 campaign units, queue 5/5 done): its queue timer disabled and the machine stopped at 13:14. Last campaign: pairs no_llm s202 on staging, expected about 15:00 UTC |
| 2026-10-22 13:45 | 25 / 1 / 0 (of 26) | Scheduled check: no attention needed. The only ATTENTION line was the staging2 probe failing because that machine is stopped (deliberately, at 13:14); no campaign affected. Still running: pairs no_llm s202 on staging (launched 02:29), expected about 15:00 UTC; the one-off check at 15:37 UTC shuts down on completion |
| 2026-10-22 15:38 | **26 / 0 / 0 (of 26): ALL TERMINAL** | Finish check: pairs no_llm s202 terminal. Staging queue timer disabled (0 active campaign units); both staging machines stopped at 15:39 (staging2 already stopped since 13:14). Recurring status check removed. No score read; collection pending the user's go |

## Collection (2026-10-22, on the user's go)

`python -m bench.eval_kit.collect --tag <tag> --ablation all` from each tag's own worktree (clean, at the tag), 16:0x UTC:
`ablations_ablation-release-a.json` (no_llm_reasoning, no_capacity_ladder) and `ablations_ablation-release-b.json` (no_second_stages,
no_method_prior). 26/26 records reportable and evidence-clean; 0 refused. Billed GPU hours per campaign from SageMaker
(`ablation_usage.json`); no cell capacity-affected under the pre-registered clause. Medal seed-runs, release -> ablated:
no_llm_reasoning 12 -> 12, no_capacity_ladder 4 -> 4, no_second_stages 3 -> 0, no_method_prior 6 -> 6. Table and summary:
`make_ablation.py` -> `tables/ablations.tex`, `ablation_summary.json`.
