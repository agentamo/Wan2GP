# Q6 120 W Recovery Baseline

Date: 2026-05-21 KST

This is the current rollback baseline for the local Wan2GP video pipeline.

If a future install, update, model change, driver change, config change, or environment change causes the computer to shut down, become unstable, or abnormally overheat, roll back to these settings and test conditions first.

## Baseline Conditions

- User-set GPU power target: 120 W
- Cooling: llano V12, baseline fan speed user-reported at 2000 RPM
- Model: LTX-2.3 22B distilled Q6 GGUF
- Resolution: 512x896
- FPS: 24
- Steps: 8
- Guidance scale: 1.0
- Audio guidance scale: 1.0
- Guidance2 scale: 1.0
- Guidance3 scale: 1.0
- Flow shift: 4.5
- Input video strength: 0.92
- Wan2GP duration_seconds: 0.0
- Duration is controlled by video_length
- No LoRA
- No RIFE
- No temporal upscale
- No spatial upscale
- No HDR
- No FlashVSR
- No postprocess

## Passing Tests

| Test | WanGP Version | Frames | Duration | Status | Peak GPU Temp | Peak GPU Power | Elapsed |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| v11.66 Q6 5s | 11.66 | 121 | 5.04s | complete | 87 C | 107.67 W | 267.8s |
| current Q6 5s | 11.70 | 121 | 5.04s | complete | 87 C | 108.22 W | 260.3s |
| current Q6 10s | 11.70 | 241 | 10.04s | complete | 88 C | 118.29 W | 346.5s |

All three no-abort tests completed and produced non-black 512x896 MP4 outputs.

## Rollback Files

Local job records:

- `C:\Users\USER\Documents\UGC_videos\ugc_jobs\recovery_v1166_q6_clockcap_test\noabort_generation_log.csv`
- `C:\Users\USER\Documents\UGC_videos\ugc_jobs\recovery_10s_compare_q6\noabort_generation_log.csv`

Settings snapshots:

- `C:\Users\USER\Documents\UGC_videos\ugc_jobs\recovery_v1166_q6_clockcap_test\settings\recovery_clockcap_v1166_q6_5s_seed_260511_noabort_120w.json`
- `C:\Users\USER\Documents\UGC_videos\ugc_jobs\recovery_10s_compare_q6\settings\recovery_energybar_oldsetup_5s_current_wangp_seed_260511_noabort_120w.json`
- `C:\Users\USER\Documents\UGC_videos\ugc_jobs\recovery_10s_compare_q6\settings\recovery_energybar_oldsetup_10s_current_wangp_seed_260511_noabort_120w.json`

Outputs:

- `C:\Users\USER\Documents\UGC_videos\ugc_jobs\recovery_v1166_q6_clockcap_test\outputs\recovery_clockcap_v1166_q6_5s_seed_260511_noabort_.mp4`
- `C:\Users\USER\Documents\UGC_videos\ugc_jobs\recovery_10s_compare_q6\outputs\recovery_energybar_oldsetup_5s_current_wangp_seed_.mp4`
- `C:\Users\USER\Documents\UGC_videos\ugc_jobs\recovery_10s_compare_q6\outputs\recovery_energybar_oldsetup_10s_current_wangp_seed.mp4`

## Operational Note

Use this baseline before trying higher duration, higher resolution, new model builds, new dependencies, driver changes, or larger batch runs. If new behavior causes shutdowns, runaway heat, or instability, restore these settings and re-run the 5-second Q6 test before moving back to 10 seconds.
