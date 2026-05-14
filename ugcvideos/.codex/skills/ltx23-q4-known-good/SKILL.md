---
name: ltx23-q4-known-good
description: Use when working in this Wan2GP checkout on the successful LTX-2.3 22B Distilled GGUF Q4_K_M Light laptop flow, especially reproducing, extending, debugging, or preserving the 10-second 241-frame test with audio.
---

# LTX-2.3 Q4 Known Good Workflow

## Start Here

Use this skill in `C:\Users\USER\Documents\UGC_videos\Wan2GP\ugcvideos` when the task mentions LTX-2.3, LTX 2.3, 22B Q4, Q4_K_M Light, 10-second tests, UGC queues, or preserving the current successful WanGP state.

Before changing anything, read:

- `ugcvideos/ltx2_laptop_test_report.md`
- `ugcvideos/test_queues/ltx23_q4_ugc_smoke/queue.json`
- `ugcvideos/scripts/download_ltx23_q4_assets.py` if assets or offline preload behavior matter

## Successful Test Snapshot

Date: 2026-05-14

Environment:

- WanGP root: `C:\Users\USER\Documents\UGC_videos\Wan2GP`
- WanGP UI version observed: `v11.66`
- GPU: NVIDIA GeForce RTX 3080 Ti Laptop GPU, 16,384 MiB VRAM
- System RAM: 64 GB
- UI was already running at `http://localhost:7860`

Known-good model and queue:

- Model: `LTX-2 2.3 Distilled 1.0 GGUF Q4_K_M Light 22B`
- Preset: `defaults/ltx2_22B_distilled_gguf_q4_k_m.json`
- Queue: `ugcvideos/test_queues/ltx23_q4_ugc_smoke/queue.json`
- Queue zip: `ugcvideos/test_queues/ltx23_q4_ugc_smoke.zip`
- Start/reference image: `ugcvideos/test_queues/ltx23_q4_ugc_smoke/ugc_golden_frame_fit_man_red_bar.png`
- Output name from queue: `LTX23_Q4_UGC_Laptop_Test`

Successful output recorded in `ugcvideos/ltx2_laptop_test_report.md`:

- Output file: `outputs/LTX23_Q4_UGC_Laptop_Test.mp4`
- Video: H.264, `448x832`, `24 fps`, `241` frames, `10.041667s`
- Audio: AAC mono, `48,000 Hz`, `10.026000s`
- Output size: `4,182,140` bytes
- WanGP process memory after completion: about `35.77 GiB` working set
- GPU memory after completion: about `306 MiB`

## Asset Rules

The lean LTX-2.3 Q4 asset downloader is:

```powershell
python ugcvideos\scripts\download_ltx23_q4_assets.py
```

The script intentionally downloads Q4_K_M Light and supporting files only. It does not fetch Q6_K unless `--include-q6` is passed.

The first autoload attempt failed while `HF_HUB_OFFLINE` was active because inherited preload assets were missing. The successful run happened after these were present locally:

- `loras/ltx2/ltx-2.3-22b-ic-lora-outpaint.safetensors`
- `loras/ltx2/ltx-2.3-22b-ic-lora-hdr-0.9.safetensors`
- `ckpts/ltx-2.3-22b-ic-lora-hdr-scene-emb.safetensors`

Do not commit model weights, generated videos, or raw generated logs unless the user explicitly asks. Queue zips under `ugcvideos/test_queues/` are intentionally preserved because they are small UI-import artifacts for known-good tests.

## Queue Settings That Worked

The 10-second smoke queue used:

- `model_type`: `ltx2_22B_distilled_gguf_q4_k_m`
- `base_model_type`: `ltx2_22B`
- `resolution`: `480x832`
- `video_length`: `241`
- `num_inference_steps`: `8`
- `guidance_scale`: `1.0`
- `NAG_scale`: `1`
- `NAG_tau`: `3.5`
- `NAG_alpha`: `0.5`
- `seed`: `230514`

WanGP emitted `448x832` even though the queue requested `480x832`; this is expected LTX/WanGP dimension adjustment, not a failure.

Distilled GGUF presets may lock inference steps to `8`. Do not assume queue-requested higher step counts will be honored.

## Quality Gotchas

- Avoid saying `golden frame` in prompts. The successful UGC smoke test produced a literal gold-frame/border artifact in later frames. Prefer `reference image` or `first image`.
- Keep motion simple for identity and product consistency: slight hand drift, product visible near face, no dramatic camera moves.
- The log warning `[GGUF][llama.cpp CUDA] kernels unavailable, using fallback` did not block generation.

## Next Safe Experiment

For Q6_K exploration, start cautiously:

- Keep `480x832`.
- First test `121` frames, about 5 seconds.
- Keep audio enabled.
- Download only `Distilled GGUF Q6_K`.
- Avoid Dev, Dev NVFP4, regular Distilled, and Q8_0 unless the user explicitly requests them.
