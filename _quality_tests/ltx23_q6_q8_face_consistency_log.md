# LTX 2.3 Q6/Q8 Face Consistency Migration Log

Started: 2026-05-14 Asia/Seoul

## Snapshot

- Repo: `C:\Users\USER\Documents\UGC_videos\Wan2GP`
- Branch: `main`
- Commit: `4a4709f756deff13318a1f936805c7d0f034927e`
- Existing working-tree notes at snapshot time: untracked `backups/`, `envs.json`, `logs/`
- WanGP version: `11.66`
- Settings version: `2.58`
- Python executable: `C:\Users\USER\miniconda3\envs\wan2gp\python.exe`
- Python version: `3.11.14`
- PyTorch version: `2.10.0+cu130`
- CUDA runtime reported by PyTorch: `13.0`
- CUDA available: `True`
- GPU: `NVIDIA GeForce RTX 3080 Ti Laptop GPU`
- Driver: `596.36`
- VRAM: `16384 MiB`

## Current Stable Fallback

- Current WanGP selected model type: `ltx2_22B_distilled_gguf_q4_k_m`
- Current working Q4 model path: `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\ltx-2.3-22b-distilled-Q4_K_M_light.gguf`
- Current Q4 model size: `12,971,904,032` bytes
- Current working settings: `settings\ltx2_22B_distilled_gguf_q4_k_m_settings.json`
- Current working Q4 preset/snapshot copied to: `_quality_tests\snapshot_20260514`
- No `.lset` files found in the repo during snapshot.

## WanGP LTX 2.3 Distilled Contract

- Loader family: `models\ltx2\ltx2_handler.py`
- Model family: `ltx2`
- LTX 2.3 base architecture: `ltx2_22B`
- Distilled pipeline: `ltx2_pipeline = distilled`
- WanGP enforces distilled settings in `validate_generative_settings`:
  - `num_inference_steps = 8`
  - `guidance_scale = 1.0`
  - `audio_guidance_scale = 1.0`
  - `alt_guidance_scale = 1.0`
  - `alt_scale = 0.0`
- NAG is available for distilled LTX 2.3 (`NAG = True`, negative prompt allowed).
- LTX 2.3 LoRA folder: `loras\ltx2`
- Compatible visible/testable LoRA preset found: `profiles\ltx2_distilled_presets\VBVR LoRA - Video Reasoning.json`

## Model Folder Structure

- WanGP checkpoint search paths from `wgp_config.json`: `ckpts`, `.`
- File locator: `shared\utils\files_locator.py`
- Built-in Q4/Q6/Q8 Light GGUF defaults expect root-level files in `ckpts` by basename.
- Requested QuantStack Q6/Q8 filenames are nested:
  - `ckpts\LTX-2.3-distilled\LTX-2.3-distilled-Q6_K.gguf`
  - `ckpts\LTX-2.3-distilled\LTX-2.3-distilled-Q8_0.gguf`
- To avoid renaming or replacing the working Q4/default models, QuantStack tests use local finetune definitions in `finetunes\`.

## Test Reference

- Reference image selected for the requested "same woman" prompt family:
  - `C:\Users\USER\Documents\UGC_videos\Wan2GP\ugcvideos\inputs\wedding_walk_reference_736x1280.png`
- Reason: existing Q4 smoke prompt/reference is a male energy-bar product test; the requested lipstick face-consistency prompt requires a woman reference.

## Q6 Status

- Q6 QuantStack target path: `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\LTX-2.3-distilled\LTX-2.3-distilled-Q6_K.gguf`
- Q6 download status: downloaded successfully with `curl.exe` resume after `huggingface_hub` stalled.
- Q6 file size: `21,006,397,248` bytes (`19.56 GiB`, approximately `21.0 GB` decimal).
- Q6 download log: `logs\ltx23_q6_quantstack_curl_resume_20260515_001341_stdout.log`
- Q6 load status: passed.
- Q6 smoke result: passed, 121 frames, `448x832`, 24 fps, AAC mono audio, generated `_quality_tests\q6_no_extra_lora_seed_230514.mp4`.
- Q6 generation time: `205.4` seconds from the API runner.
- Q6 face consistency result: passed in sampled frames 0/30/60/90/120; same woman, stable facial structure, no severe identity drift. More hand occlusion than Q4, but not a failure.
- Q6 LoRA result: pending

## Q4 Baseline Result

- Output: `_quality_tests\baseline_q4_face_test.mp4`
- Actual output geometry: `448x832` at 24 fps, 121 frames. WanGP normalized the requested `480x832` width to a model-compatible width.
- Audio: AAC mono, present.
- Visual note from sampled frames 0/30/60/90/120: strong face stability, clean lipstick action, same hairstyle and dress. Minor expression/eye variation only.
- Scores:
  - Face consistency: `4/5`
  - Motion quality: `4/5`
  - Prompt adherence: `4/5`
  - UGC realism: `4/5`
  - Audio quality: `4/5`
  - Overall keeper score: `4/5`

## Q6 No Extra LoRA Result

- Output: `_quality_tests\q6_no_extra_lora_seed_230514.mp4`
- Actual output geometry: `448x832` at 24 fps, 121 frames.
- Audio: AAC mono, present.
- Visual note from sampled frames 0/30/60/90/120: same identity holds across the clip. Eyes and nose remain stable; final frame changes head angle but still reads as the same person. Hands/product action is visible with some occlusion.
- Scores:
  - Face consistency: `4/5`
  - Motion quality: `4/5`
  - Prompt adherence: `4/5`
  - UGC realism: `4/5`
  - Audio quality: `4/5`
  - Overall keeper score: `4/5`

## Q6 241-Frame Result

- Output: `_quality_tests\q6_no_extra_lora_241_seed_230514.mp4`
- Actual output geometry: `448x832` at 24 fps, 241 frames, 10.04 seconds.
- Audio: AAC mono, present.
- Generation time: `335.2` seconds from the API runner.
- Visual note from sampled frames 0/60/120/180/240: identity holds well through 10 seconds. Face stays the same person; no severe morph after frame 30. Eyes remain close to the same shape. Final frame changes expression/hairline slightly but stays usable.
- Scores:
  - Face consistency: `4/5`
  - Motion quality: `4/5`
  - Prompt adherence: `4/5`
  - UGC realism: `4/5`
  - Audio quality: `4/5`
  - Overall keeper score: `4/5`

## Q6 LoRA Result

- VBVR LoRA file downloaded to `loras\ltx2\Ltx2.3-Licon-VBVR-I2V-96000-R32.safetensors`.
- Test output: none.
- Result: failed before video output with WanGP error: likely insufficient RAM and/or reserved RAM allocation.
- Decision: do not use VBVR or additional camera/motion LoRAs with Q6 on this laptop preset until RAM/profile tuning is done. Best LoRA combination for now is no extra LoRA.

## Q8 Result

- Q8 QuantStack target path: `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\LTX-2.3-distilled\LTX-2.3-distilled-Q8_0.gguf`
- Q8 download status: downloaded successfully with `curl.exe` resume.
- Q8 file size: `25,499,062,080` bytes (`23.75 GiB`, approximately `25.5 GB` decimal).
- Q8 smoke output: `_quality_tests\q8_smoke_seed_230514.mp4`
- Actual output geometry: `448x832` at 24 fps, 81 frames, 3.38 seconds.
- Audio: AAC mono, present.
- Generation time: `172.2` seconds from the API runner.
- Visual note from sampled frames 0/20/40/60/80: face is stable, but the output stays close to the full-body wedding reference and does not follow the requested closeup lipstick/selfie action. Prompt adherence is worse than Q4/Q6 under identical settings.
- Scores:
  - Face consistency: `4/5`
  - Motion quality: `3/5`
  - Prompt adherence: `2/5`
  - UGC realism: `3/5`
  - Audio quality: `4/5`
  - Overall keeper score: `3/5`

## Q8 Gate

Q8 will not be downloaded unless Q6:

1. Loads successfully.
2. Completes at least one 121-frame test.
3. Scores better than or equal to Q4 on face consistency.
4. Avoids severe CUDA memory errors.
5. Produces a non-corrupted video.
6. Keeps the audio pipeline usable.
