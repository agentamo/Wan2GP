# Couple 30 FPS Q4/Q6 Batch Report

Run date: 2026-05-15

Reference image:
`C:\Users\USER\Documents\UGC_videos\Wan2GP\ugcvideos\inputs\couple_red_studio_reference_20260505.png`

Prompt:
`Playful romantic couple image to video, same young couple from the reference image, bright red studio background, white formal outfits, girl playfully teases the man, man smiles with amused reaction, natural affectionate movement, soft head turns, subtle hand movement, cute couple commercial style, final moment the girl kisses the man on the cheek, then turns slightly toward the camera and says "He'sss all mineee," playful elongated syllables, both smile at the end, photorealistic, clean studio lighting, stable faces, identity consistency, smooth motion.`

Negative prompt:
`slow motion, cinematic slow motion, frozen pose, held pose, stiff body, identity drift, changing face, different person, face morphing, distorted eyes, uneven eyes, broken mouth, waxy skin, plastic skin, distorted hands, extra fingers, missing fingers, duplicated face, blurry face, product disappearing, red background changing, outfit changing, heavy cinematic lighting`

Common settings:
- Mode: image-to-video start image
- Resolution request: `640x480`
- Actual output: `640x448`
- Frames: `449`
- FPS: `30`
- Duration: `14.97s`
- Steps: `8`
- Guidance: `1.0`
- Audio generation: disabled
- LoRAs: none
- Seed: `240501`
- Q8: removed from `ckpts\LTX-2.3-distilled` and removed from WebUI finetunes

## Test Matrix

| Test | Model | Change | Temporal | Time | Output |
|---|---|---|---|---:|---|
| 01 | Q4_K_M Light | source strength `1.0` | none | 386.0s | `couple_t01_q4_30fps_native_strength100_seed_240501.mp4` |
| 02 | Q4_K_M Light | source strength `0.9` | none | 339.1s | `couple_t02_q4_30fps_native_strength090_seed_240501.mp4` |
| 03 | Q4_K_M Light | source strength `0.8` | none | 332.7s | `couple_t03_q4_30fps_native_strength080_seed_240501.mp4` |
| 04 | Q4_K_M Light | real-time motion prompt, strength `0.9` | none | 338.7s | `couple_t04_q4_30fps_realtime_strength090_seed_2405.mp4` |
| 05 | Q4_K_M Light | real-time + face-lock prompt, strength `0.9` | none | 336.6s | `couple_t05_q4_30fps_facelock_strength090_seed_2405.mp4` |
| 06 | Q4_K_M Light | real-time prompt, strength `0.9` | RIFE x2, 15 -> 30 fps | 208.7s | `couple_t06_q4_rife2_15to30_strength090_seed_240501.mp4` |
| 07 | Q6_K | source strength `1.0` | none | 462.3s | `couple_t07_q6_30fps_native_strength100_seed_240501.mp4` |
| 08 | Q6_K | source strength `0.9` | none | 437.8s | `couple_t08_q6_30fps_native_strength090_seed_240501.mp4` |
| 09 | Q6_K | real-time motion prompt, strength `0.9` | none | 414.9s | `couple_t09_q6_30fps_realtime_strength090_seed_2405.mp4` |
| 10 | Q6_K | real-time prompt, strength `0.9` | RIFE x2, 15 -> 30 fps | 265.7s | `couple_t10_q6_rife2_15to30_strength090_seed_240501.mp4` |

## Notes

- All 10 runs completed successfully.
- Q4 was tested first, as requested.
- Q8 was not used.
- RIFE x2 tests finished faster because they generated fewer base frames at 15 fps, then interpolated to 30 fps.
- WanGP shortened two long filenames on disk, ending them with `seed_2405.mp4`.

