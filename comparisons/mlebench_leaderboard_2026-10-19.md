# MLE-bench

Code for the paper ["MLE-Bench: Evaluating Machine Learning Agents on Machine Learning Engineering"](https://arxiv.org/abs/2410.07095). We have released the code used to construct the dataset, the evaluation logic, as well as the agents we evaluated for this benchmark.

## Leaderboard
*Update* (04-24-2026): We are currently not taking any new submissions to the leaderboard while we develop an improved process for ensuring submissions are fair and comparable. We will share updates on this process in the future.

| Agent | LLM(s) used | Low == Lite (%) | Medium (%) | High (%) | All (%) | Running Time (hours) | Date | Source Code Available | Grading Reports Available |
|-------|-------------|-----------------|------------|----------|---------|----------------------|------|----------------------|---------------------------|
| [Famou-Agent 2.0](https://github.com/baidubce/FM-Agent) | Gemini-3-Pro-Preview | 80.3 ± 1.52 | 64.04 ± 2.32 | 42.22 ± 2.22 | 64.44 ± 1.18 | 24 | 2026-02-23 | X | ✓ |
| [AIBuildAI](https://github.com/aibuildai/AI-Build-AI) | Claude-Opus-4.6 |  77.27 ± 0.00 |  61.40 ± 0.88 |  46.67 ± 0.00 | 63.11 ± 0.44 | 24 | 2026-03-06 | X | ✓ |
| [CAIR](https://research.google/teams/cloud-ai-research/) [MARS+](https://arxiv.org/pdf/2602.02660) | Gemini-3-Pro-Preview | 78.79 ± 1.52 | 60.53 ± 1.52 | 44.44 ± 2.22 | 62.67 ± 0.77 | 24 | 2026-02-17 | X | ✓ |
| [MLEvolve](https://github.com/InternScience/MLEvolve) | Gemini-3-Pro-Preview | 80.30 ± 1.52 | 57.89 ± 1.52 | 42.22 ± 2.22 | 61.33 ± 1.33 | 12 | 2026-02-14 | ✓ | ✓ |
| [PiEvolve](https://github.com/FractalAIResearchLabs/PiEvolve)<br>(Fractal AI Research) | Gemini-3-Pro-Preview[^4] | 80.30 ± 1.52[^3] | 58.77 ± 0.88[^3] | 40.0 ± 0.00[^3] | 61.33 ± 0.77[^3] | 24 | 2026-01-05 | X | ✓ |
| [Famou-Agent 2.0](https://github.com/baidubce/FM-Agent) | Gemini-2.5-Pro | 75.76 ± 1.52 | 57.89 ± 1.52 | 40.00 ± 0.00 | 59.56 ± 0.89 | 24 | 2025-12-27 | X | ✓ |
| [ML-Master 2.0](https://github.com/sjtu-sai-agents/ML-Master) | Deepseek-V3.2-Speciale | 75.76 ± 1.51 | 50.88 ± 3.51 | 42.22 ± 2.22 | 56.44 ± 2.47 | 24 | 2025-12-16 | X | ✓ |
| [CAIR](https://research.google/teams/cloud-ai-research/) [MARS](https://arxiv.org/pdf/2602.02660) | Gemini-3-Pro-Preview | 74.24 ± 1.52  | 52.63  ±  3.04 | 37.78 ± 2.22  | 56.0 ± 1.54 | 24 | 2026-01-25 | X | ✓ |
| [PiEvolve](https://github.com/FractalAIResearchLabs/PiEvolve)<br>(Fractal AI Research) | Gemini-3-Pro-Preview[^4] | 74.24 ± 3.03[^3] | 45.61 ±  0.88[^3] | 35.55 ± 2.22[^3] | 52.0 ±  0.77[^3] | 12 | 2026-01-05 | X | ✓ |
| [Leeroo](https://github.com/Leeroo-AI/kapso) | Gemini-3-Pro-Preview[^4] | 68.18 ± 2.62[^3] | 44.74 ± 1.52[^3] | 40.00 ± 0.00[^3] | 50.67 ± 1.33[^3] | 24 | 2025-12-07 | ✓ | ✓ |
| [Thesis](https://thesislabs.ai) | gpt-5-codex | 65.15 ± 1.52 | 45.61 ± 7.18 | 31.11 ± 2.22 | 48.44 ± 3.64 | 24 | 2025-11-10 | X | ✓ |
| [CAIR](https://research.google/teams/cloud-ai-research/) MLE-STAR-Pro-1.5 | Gemini-2.5-Pro | 68.18 ± 2.62 | 34.21 ± 1.52  |  33.33 ±  0.00 |  44.00 ± 1.33 | 24 | 2025-11-25 | X | ✓ |
| [Famou-Agent](https://github.com/baidubce/FM-Agent) | Gemini-2.5-Pro | 62.12 ± 1.52 | 36.84 ± 1.52 | 33.33 ± 0.00 | 43.56 ± 0.89 | 24 | 2025-10-10 | X | ✓ |
| [Operand](https://operand.com) ensemble | gpt-5 (low verbosity/effort)[^2] | 63.64 ± 0.00 | 33.33 ± 0.88[^3] | 20.00 ± 0.00[^3] | 39.56 ± 0.44[^3] | 24 | 2025-10-06 | X | ✓ |
| [CAIR](https://research.google/teams/cloud-ai-research/) MLE-STAR-Pro-1.0 | Gemini-2.5-Pro | 66.67 ± 1.52  | 25.44  ±  0.88 | 31.11 ± 2.22  | 38.67 ± 0.77 | 12 | 2025-11-03 | X | ✓ |
| [InternAgent](https://github.com/Alpha-Innovator/InternAgent/) | deepseek-r1 | 62.12 ± 3.03 | 26.32 ± 2.63 | 24.44 ± 2.22 | 36.44 ± 1.18 | 12 | 2025-09-12 | X | ✓ |
| [R&D-Agent](https://github.com/microsoft/RD-Agent) | gpt-5 | 68.18 ± 2.62 | 21.05 ± 1.52 | 22.22 ± 2.22 | 35.11 ± 0.44 | 12 | 2025-09-26 | ✓ | ✓ |
| [Neo](https://heyneo.so/) multi-agent | undisclosed | 48.48 ± 1.52 | 29.82 ± 2.32 | 24.44 ± 2.22 | 34.22 ± 0.89 | 36 | 2025-07-28 | X | ✓ |
| [AIRA-dojo](https://github.com/facebookresearch/aira-dojo/) | o3 | 55.00 ± 1.47 | 21.97 ± 1.17 | 21.67 ± 1.07 | 31.60 ± 0.82 | 24 | 2025-05-15 | ✓ | ✓ |
| [R&D-Agent](https://github.com/microsoft/RD-Agent) | o3 + GPT-4.1 | 51.52 ± 4.01 | 19.30 ± 3.16 | 26.67 ± 0.00 | 30.22 ± 0.89 | 24 | 2025-08-15 | ✓ | ✓ |
| [ML-Master](https://github.com/zeroxleo/ML-Master) | deepseek-r1 | 48.48 ± 1.52 | 20.18 ± 2.32 | 24.44 ± 2.22 | 29.33 ± 0.77 | 12 | 2025-06-17 | ✓ | ✓ |
| [R&D-Agent](https://github.com/microsoft/RD-Agent) | o1-preview | 48.18 ± 1.11 | 8.95 ± 1.05 | 18.67 ± 1.33 | 22.40 ± 0.50 | 24 | 2025-05-14 | ✓ | ✓ |
| [AIDE](https://github.com/wecoai/aideml) | o1-preview | 35.91 ± 1.86 | 8.45 ± 0.43 | 11.67 ± 1.27 | 17.12 ± 0.61 | 24 | 2024-10-08 | ✓ | ✓ |
| [AIDE](https://github.com/wecoai/aideml) | gpt-4o-2024-08-06 | 18.55 ± 1.26 | 3.06 ± 0.33 | 8.15 ± 0.84 | 8.63 ± 0.54 | 24 | 2024-10-08 | ✓ | ✓ |
| [AIDE](https://github.com/wecoai/aideml) | claude-3-5-sonnet-20240620 | 19.70 ± 1.52 | 2.63 ± 1.52 | 2.22 ± 2.22 | 7.56 ± 1.60 | 24 | 2024-10-08 | ✓ | ✓ |
| OpenHands | gpt-4o-2024-08-06 | 12.12 ± 1.52 | 1.75 ± 0.88 | 2.22 ± 2.22 | 4.89 ± 0.44 | 24 | 2024-10-08 | ✓ | ✓ |
| [AIDE](https://github.com/wecoai/aideml) | llama-3.1-405b-instruct | 10.23 ± 1.14 | 0.66 ± 0.66 | 0.00 ± 0.00 | 3.33 ± 0.38 | 24 | 2024-10-08 | ✓ | ✓ |
| MLAB | gpt-4o-2024-08-06 | 4.55 ± 0.86 | 0.00 ± 0.00 | 0.00 ± 0.00 | 1.60 ± 0.27 | 24 | 2024-10-08 | ✓ | ✓ |

### Additional Leaderboard Submissions

