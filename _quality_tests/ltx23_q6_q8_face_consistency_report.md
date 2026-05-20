# LTX 2.3 Q6/Q8 Face Consistency Report

Date: 2026-05-15 Asia/Seoul

## Summary

Recommended laptop preset: **LTX 2.3 Distilled GGUF Q6_K QuantStack, no extra LoRA, 480x832 requested, 121-241 frames, 8 steps, guidance 1.0, fixed seed as needed**.

Q6 is the best next step over the current Q4 fallback. Q8 loads and completes a short smoke test, but it does not improve the result enough to justify the extra memory/time on this laptop: with the same prompt/start image it stayed close to the full-body reference and missed the closeup lipstick UGC action.

## Snapshot

- Repo: `C:\Users\USER\Documents\UGC_videos\Wan2GP`
- Branch/commit: `main`, `4a4709f756deff13318a1f936805c7d0f034927e`
- WanGP: `v11.66`
- Python: `3.11.14`
- PyTorch/CUDA: `2.10.0+cu130`, CUDA runtime `13.0`
- GPU/driver: `NVIDIA GeForce RTX 3080 Ti Laptop GPU`, driver `596.36`, `16384 MiB` VRAM
- Snapshot folder: `_quality_tests\snapshot_20260514`

## Baseline Q4 Result

- Model: `ltx2_22B_distilled_gguf_q4_k_m`
- Model file: `ckpts\ltx-2.3-22b-distilled-Q4_K_M_light.gguf`
- Output: `_quality_tests\baseline_q4_face_test.mp4`
- Actual output: `448x832`, 121 frames, 24 fps, AAC mono audio
- Result: stable same-person face, good closeup lipstick action, usable UGC look.
- Scores: face `4/5`, motion `4/5`, prompt `4/5`, UGC realism `4/5`, audio `4/5`, overall `4/5`

## Q6 Status

- Download: passed
- Model file: `ckpts\LTX-2.3-distilled\LTX-2.3-distilled-Q6_K.gguf`
- Size: `21,006,397,248` bytes, about `21.0 GB`
- WanGP model type: `ltx2_22B_distilled_gguf_q6_k_quantstack`
- Load/smoke: passed
- 121-frame output: `_quality_tests\q6_no_extra_lora_seed_230514.mp4`
- 241-frame output: `_quality_tests\q6_no_extra_lora_241_seed_230514.mp4`
- Generation time: `205.4s` for 121 frames, `335.2s` for 241 frames
- Best settings: no extra LoRA, `num_inference_steps=8`, `guidance_scale=1.0`, `audio_guidance_scale=1.0`, `input_video_strength=1.0`, NAG negative prompt enabled
- Best LoRA combination: **none beyond required/system handling**
- Q6 improves over Q4: **yes enough to adopt as the quality preset**, with similar face stability and slightly richer sampled closeups. Q4 remains the fallback.
- Scores: face `4/5`, motion `4/5`, prompt `4/5`, UGC realism `4/5`, audio `4/5`, overall `4/5`

## LoRA Test

- VBVR preset was visible in `profiles\ltx2_distilled_presets\VBVR LoRA - Video Reasoning.json`.
- Downloaded file: `loras\ltx2\Ltx2.3-Licon-VBVR-I2V-96000-R32.safetensors`
- Q6 + VBVR failed before output with WanGP RAM/reserved-RAM warning.
- Decision: do not use VBVR/camera LoRAs with Q6 on this laptop until memory profile tuning is done.

## Q8 Status

- Download: passed
- Model file: `ckpts\LTX-2.3-distilled\LTX-2.3-distilled-Q8_0.gguf`
- Size: `25,499,062,080` bytes, about `25.5 GB`
- WanGP model type: `ltx2_22B_distilled_gguf_q8_0_quantstack`
- Smoke output: `_quality_tests\q8_smoke_seed_230514.mp4`
- Actual output: `448x832`, 81 frames, 24 fps, AAC mono audio
- Generation time: `172.2s` for 81 frames
- Result: stable face, but worse prompt adherence. It stayed near the full-body wedding reference instead of moving into closeup lipstick UGC.
- Q8 improves over Q6 enough to justify memory/time: **no**
- Scores: face `4/5`, motion `3/5`, prompt `2/5`, UGC realism `3/5`, audio `4/5`, overall `3/5`

## Reproduce Best Result

Use WanGP model:

`LTX-2 2.3 Distilled GGUF Q6_K QuantStack 22B`

Exact local model definition:

`finetunes\ltx2_22B_distilled_gguf_q6_k_quantstack.json`

Exact settings file:

`_quality_tests\settings_q6_241_face_test.json`

API command used:

```powershell
& 'C:\Users\USER\miniconda3\envs\wan2gp\python.exe' `
  'C:\Users\USER\Documents\UGC_videos\Wan2GP\_quality_tests\run_wangp_task.py' `
  --settings 'C:\Users\USER\Documents\UGC_videos\Wan2GP\_quality_tests\settings_q6_241_face_test.json' `
  --copy-to 'q6_no_extra_lora_241_seed_230514.mp4'
```

Important UI values:

- Model: `ltx2_22B_distilled_gguf_q6_k_quantstack`
- Start image: `ugcvideos\inputs\wedding_walk_reference_736x1280.png`
- Resolution requested: `480x832` (WanGP output normalized to `448x832`)
- Frames: `121` for short tests, `241` for 10-second keeper test
- Steps: `8`
- Guidance: `1.0`
- Audio guidance: `1.0`
- Start Image / Source Strength: `1.0`
- LoRAs: none
- Seed: `230514`

## Next Step

Stay on Q6 for face-stability work at 480x832. Do not move to 720p until Q6/no-LoRA has produced a few more keeper clips with different face references. Keep Q4 as the fallback preset and treat Q8 as a stress-test option, not the laptop default.
