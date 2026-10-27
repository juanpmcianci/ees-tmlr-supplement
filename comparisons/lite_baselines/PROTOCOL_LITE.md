# MLE-bench Lite: direct baselines (addendum to PROTOCOL.md)

Status: **FROZEN 2026-10-16** (git tag `lite-protocol-frozen`) before the first Lite run. Changes after this go in the Amendment log below with a reason.

Requested on 2026-10-16: "run mle-bench lite in parallel… on simpler machines without GPUs… need not run for longer duration… make reasonable adjustments as required on duration length and infra."

Everything in PROTOCOL.md applies, **except** where this addendum says otherwise.

## Tasks
MLE-bench Lite is the official Low split, `experiments/splits/low.txt` at mle-bench commit `507f92e1138bb6e40dac5c6ee7a6758e6424bf97`. It has 22 competitions (about 158 GB in total):

aerial-cactus-identification, aptos2019-blindness-detection, denoising-dirty-documents, detecting-insults-in-social-commentary, dog-breed-identification, dogs-vs-cats-redux-kernels-edition, histopathologic-cancer-detection, jigsaw-toxic-comment-classification-challenge, leaf-classification, mlsp-2013-birds, new-york-city-taxi-fare-prediction, nomad2018-predict-transparent-conductors, plant-pathology-2020-fgvc7, random-acts-of-pizza, ranzcr-clip-catheter-line-classification, siim-isic-melanoma-classification, spooky-author-identification, tabular-playground-series-dec-2021, tabular-playground-series-may-2022, text-normalization-challenge-english-language, text-normalization-challenge-russian-language, the-icml-2013-whale-challenge-right-whale-redux.

The task list comes from the mle-bench repo only. The operator does not read the authors' public results README, notes or results (ground rule 1).

There is one run per task per baseline, so 44 runs.

## What differs from High
| Item | High (PROTOCOL.md) | Lite |
|---|---|---|
| Machine | g6e.12xlarge, 4× L40S | **m7i.8xlarge: 32 vCPU, 128 GB RAM, no GPU**, with an EBS gp3 data volume of at least 3× the largest Lite dataset. Same type for every Lite run. |
| Time limit | 24 h | **6 h wall clock** per run, with a hard stop. The MLE-bench README allows reduced runtime and compute for Lite and notes that it can lower scores. |
| Prompt header | "You have 24 hours … (g6e.12xlarge, 4x NVIDIA L40S)" | "You have 6 hours of wall-clock time on this machine (m7i.8xlarge, 32 vCPUs, 128 GB RAM, no GPU). Work autonomously; no human will answer questions. Your final submission must be at /home/submission/submission.csv before the deadline." |
| Continue message | unchanged | unchanged ("You still have <H> hours left…") |
| Region | us-east-2 | us-east-2 first, then us-east-1 and us-west-2 if CPU quota allows. The data is always read from the us-east-2 public bucket. |
| Watchdog | 27 h | 9 h after the run starts |

These stay the same as High: the Docker image (`mlebench-bl/run:v1`), the CLIs and pinned versions, the models (`claude-fable-5-1` and `gpt-6-luna`), effort `max`, web search on, instructions.txt and description.md verbatim, the format-only validator, the isolation check before every run, the leakage and solution-viewing flags, the re-invocation rules, the logging, and grading once at the end with `mlebench grade-sample`.

## Queue and priority
- The Lite queue runs on its own CPU machines, in parallel with High, and never competes for GPU capacity.
- Lite runs are queued in split order, alternating Claude and Codex within each task.
- Hosts are reused between Lite runs, the same way as for High: fresh container, data and work directories wiped.

## Reporting
The Lite results get their own table, in the same format as High: medal, score, thresholds, wall time, $ cost, re-invocations and flags. The GPU-hours column reads "CPU-only". The report also gives the Lite medal rate per baseline.

## Amendment log
| Date | Change | Reason |
|---|---|---|
| 2026-10-17 | Controller fix, applied to runs that start after 01:58 UTC 2026-10-17: (1) "an agent-started process is still running" now means a process owned by the agent user; the root-owned validator is no longer counted. (2) The "said it is finished" phrase detector also recognises "remains the best/final/in place", "no further change is warranted/supported", "kept … unchanged". | lite__denoising-dirty-documents__codex: the agent re-confirmed a finished submission over 16 re-invocations, because its wording wasn't recognised as "finished". Then, after two recognised claims, the controller held the idle machine because it counted the validator's helper shell as agent work. The operator released that run at 01:53 by stopping the validator in its container; it then finalised normally. Its submission was unchanged since 00:31 and is unaffected. Runs already in progress keep the old controller; the operator watches them for the same stall and releases them the same way. |
| 2026-10-17 | detecting-insults-in-social-commentary and the-icml-2013-whale-challenge-right-whale-redux are deferred: not run for now, and Lite is reported over the 20 tasks that have data. | Kaggle still refuses their data (rules not accepted on the token's account). Requester: "forget about those two for now". If they are run later, they follow this protocol unchanged. |
| 2026-10-17 | Claude runs hit by the Anthropic credit outage (credit exhausted about 03:18 UTC to about 18:10 UTC 2026-10-17; every call returned "Credit balance is too low") are **rerun** under new run IDs with suffix `__r2`. The rerun is the primary result for that task × baseline. The original runs are kept, graded with everything else, and reported in a separate "infrastructure-affected" section. Nothing is deleted. Lite runs affected: aptos2019-blindness-detection, denoising-dirty-documents, dog-breed-identification, dogs-vs-cats-redux-kernels-edition, histopathologic-cancer-detection, jigsaw-toxic-comment-classification-challenge (all Claude). | The outage came from the study's own API billing, not from the agent. The originals lost 1.4–5.7 h of agent time (Lite) and about 12.5 h (High). The requester decided on 2026-10-17 ("yes rerun") **before any run was graded and before any score was seen**. This deliberately goes beyond the frozen relaunch rule (infra failure before a submission): the originals did produce submissions. |
| 2026-10-18 | **Standing rerun rule:** any run that lost more than 10% of its time limit to an API-credit outage gets an `__r2` rerun. For Lite that is more than 36 min; for High, more than 2.4 h. The rerun is the primary result, and the original is reported as infrastructure-affected. Second outage (Anthropic credit exhausted about 23:04 UTC 2026-10-17 to about 05:45 UTC 2026-10-18) → Lite Claude reruns for aerial-cactus-identification (20% lost), mlsp-2013-birds (19%), new-york-city-taxi-fare-prediction (19%), nomad2018-predict-transparent-conductors (20%), plant-pathology-2020-fgvc7 (20%), ranzcr-clip-catheter-line-classification (20%), siim-isic-melanoma-classification (25%), spooky-author-identification (23%), tabular-playground-series-dec-2021 (25%), tabular-playground-series-may-2022 (89%), text-normalization-challenge-english-language (100%). Not rerun: leaf-classification and random-acts-of-pizza (0% lost). | Requester, 2026-10-18: "first finish all lite tasks with claude", given before any grading or scores, following the earlier "yes rerun" decision. Codex runs were never affected by either outage. |
| 2026-10-18 | **Regrade of all Lite runs with MLE-bench's environment versions pinned** (pandas 2.2.2, scikit-learn 1.5.1, numpy 1.26.4, scipy 1.14.1, tensorflow 2.17.0, from `environment/requirements.txt` at the pinned commit). The first grading pass (18:06 UTC) resolved pandas 3.x / scikit-learn 1.9+, because mle-bench's pyproject only lower-bounds them. Under pandas 3 the text-normalization grader crashed ("'<' not supported between instances of 'str' and 'float'") on a submission whose ids and row count match the answers exactly. All 57 runs are regraded uniformly; v2 grades are primary, and v1 grades are kept in S3 (`runs/<id>/grade.json`) and reported. | Grading-infrastructure fault, not agent behaviour. Every run is regraded the same way, so no run is selectively re-scored. |
| 2026-10-18 | **Known limitation of the format-only validator (disclosed, not correctable after the fact):** it only recognised sample files named `sample_submission*`. On denoising-dirty-documents (`sampleSubmission.csv`), random-acts-of-pizza (`sampleSubmission.csv`) and both text-normalization tasks (`en_/ru_sample_submission_2.csv.zip`) it answered "Submission is valid." without checking anything. This affected both baselines identically. | Operator bug, found while reviewing grading output. Reported in the fairness notes. |
