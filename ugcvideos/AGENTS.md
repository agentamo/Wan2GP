# UGC Videos Agent Notes

## Orientation

- Treat `C:\Users\USER\Documents\UGC_videos\Wan2GP` as the project root. The parent `UGC_videos` folder is a workspace wrapper, not the git repository.
- Treat `ugcvideos/` as the home for this UGC preservation project inside `agentamo/Wan2GP`.
- Preserve local model weights, generated videos, and logs unless the user explicitly asks to prune them. The repository `.gitignore` intentionally ignores heavy outputs such as `ckpts/`, `loras/`, `outputs/`, `*.mp4`, `*.safetensors`, and `*.zip`.
- When working on LTX-2 or LTX-2.3 UGC tests, read `ugcvideos/ltx2_laptop_test_report.md` first. It is the current source of truth for successful laptop runs.
- Project-local Codex skill guidance lives in `ugcvideos/.codex/skills/ltx23-q4-known-good/SKILL.md`. Use it before reproducing, extending, or debugging the successful LTX-2.3 Q4 10-second flow.

## Known Good LTX-2.3 State

The preserved successful run is the LTX-2.3 22B Distilled 1.0 GGUF Q4_K_M Light laptop smoke test from 2026-05-14.

- Model preset: `defaults/ltx2_22B_distilled_gguf_q4_k_m.json`
- Queue: `ugcvideos/test_queues/ltx23_q4_ugc_smoke/queue.json`
- Queue zip: `ugcvideos/test_queues/ltx23_q4_ugc_smoke.zip`
- Reference image: `ugcvideos/test_queues/ltx23_q4_ugc_smoke/ugc_golden_frame_fit_man_red_bar.png`
- Output captured in the report: `outputs/LTX23_Q4_UGC_Laptop_Test.mp4`
- Successful output spec: H.264, `448x832`, `24 fps`, `241` frames, `10.041667s`, AAC mono audio at `48,000 Hz`
- WanGP accepted `480x832` in the queue and emitted `448x832`; this dimension adjustment is expected.
- Distilled GGUF runs used locked `8` inference steps even when queues carried higher values.

## Repro Notes

- Use `python ugcvideos\scripts\download_ltx23_q4_assets.py` from the Wan2GP root to fetch the lean LTX-2.3 Q4 asset set. Do not download Q6 unless the user asks or is intentionally running the next test.
- `HF_HUB_OFFLINE` can block autoload if inherited preload assets are missing. The successful LTX-2.3 run required the inherited outpaint LoRA, HDR LoRA, and HDR scene embedding to be present locally.
- Avoid prompt wording such as `golden frame` for quality reruns. It created a literal gold border artifact; say `reference image` or `first image` instead.
- The GGUF CUDA fallback warning did not block the successful render, but it may affect performance.

## Commit Hygiene

- Before staging, run `git status --short --untracked-files=all` from the project root and inspect untracked folders carefully.
- Prefer explicit `git add` paths. Avoid `git add -A` here because the workspace commonly contains ignored or generated media artifacts.
- Dotfiles and zips are ignored by the root `.gitignore`; use `git add -f ugcvideos/.codex/... ugcvideos/test_queues/*.zip` only for intentional project-local agent, skill, or queue-import artifacts.
