# Stable Rollback Notes - Energy Bar Q6

Rollback target selected from stable completed logs: `energy_bar_ladder_t11_q6_15s_flow45_crisper_motion_wincompat.mp4`.

Reason: user described best motion, lip sync, and realism. The exact filename was not visible in the latest message, so this is the closest matching stable candidate from the completed ladder.

Stable settings to keep:
- WanGP only, no ComfyUI.
- Model: `ltx2_22B_distilled_gguf_q6_k`.
- Resolution: `512x896`.
- Aspect/crop: `fit_canvas=2`.
- FPS: `24`.
- Frames: `361` for 15.04 seconds.
- Steps: `8` locked distilled default.
- Guidance: `1.0` distilled default.
- Image prompt type: `S` start image only.
- Start image: `_quality_tests\kling_energy_bar_first_frame.png`.
- End image: none.
- LoRAs: none.
- Temporal upsampling/RIFE: none.
- Spatial upsampling: none.
- Flow shift: `4.5` for t11, or `5.0` for t08-t10 stable variants.
- Input video/image strength: `0.92` for t11.
- Output codec: `libx264_8`, then Windows-compatible H.264/AAC transcode.

Do not do next:
- Do not use `flow_shift=5.5`; t12 completed but took 1645 seconds and preceded the first crash window.
- Do not use `image_prompt_type=SE` or end-image guidance yet; the next unwrap runner crashed before completing its first trial.
- Do not use multiple anchor/end images or injected visual-state guidance until laptop stability is proven.
- Do not run 10 long tests unattended.
- Do not use RIFE for 15s clips; earlier RIFE was impractically slow.
- Do not use Q8.
- Do not use VBVR LoRA on Q6; earlier RAM/reserved-memory failure.
- Do not switch to 736x1280/720p yet.
- Do not use 75-second generation/prompt relay locally.

Crash notes:
- Stable t08-t11 completed normally around 469-475 seconds each.
- t12 with `flow_shift=5.5` completed but took 1645 seconds.
- Crash happened after t13 started in the old ladder.
- New unwrap runner crashed before finishing trial 21, before any output. It introduced a much longer state-machine prompt and planned SE/end-image trials, so this whole runner is marked unsafe.
- Current Windows config was changed to High Performance, AC sleep/display/hibernate disabled.
- Current WanGP config is rolled back to Q6 + 512x896 + fit_canvas=2.
