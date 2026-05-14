# LTX-2 Laptop Q4 Smoke Test Report

Date: 2026-05-14
WanGP install: `C:\Users\USER\Documents\UGC_videos\Wan2GP`
WanGP version shown in UI: `v11.66`
Archived UGC project location in git: `ugcvideos/`

## Hardware

- CPU: AMD Ryzen 9 6900HX
- RAM: 64 GB system RAM
- GPU: NVIDIA GeForce RTX 3080 Ti Laptop GPU
- VRAM: 16,384 MiB
- NVIDIA driver: 596.36

## WanGP Storage And Downloader

- Primary model storage: `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts`
- LTX-2 LoRA storage: `C:\Users\USER\Documents\UGC_videos\Wan2GP\loras\ltx2`
- Output storage: `C:\Users\USER\Documents\UGC_videos\Wan2GP\outputs`
- Q4 preset: `C:\Users\USER\Documents\UGC_videos\Wan2GP\defaults\ltx2_distilled_gguf_q4_k_m.json`
- LTX-2 shared asset manifest: `C:\Users\USER\Documents\UGC_videos\Wan2GP\models\ltx2\ltx2_handler.py`
- WanGP download helpers: `C:\Users\USER\Documents\UGC_videos\Wan2GP\shared\utils\download.py`
- WanGP path resolver: `C:\Users\USER\Documents\UGC_videos\Wan2GP\shared\utils\files_locator.py`

WanGP was already running on `http://localhost:7860`. I did not change ports.

## Model Variant Downloaded

Exact selected model:

`LTX-2 2.0 19B Distilled GGUF Q4_K_M`

Q4 URL from WanGP preset:

`https://huggingface.co/Kijai/LTXV2_comfy/resolve/main/diffusion_models/ltx-2-19b-distilled_Q4_K_M.gguf`

Not downloaded:

- Dev
- Dev NVFP4
- regular Distilled diffusion checkpoint
- Distilled GGUF Q6_K
- Distilled GGUF Q8_0

## Downloaded File Paths

| File | Bytes |
| --- | ---: |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\ltx-2-19b-distilled_Q4_K_M.gguf` | 12,651,789,536 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\ltx-2-spatial-upscaler-x2-1.0.safetensors` | 995,765,578 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\ltx-2-temporal-upscaler-x2-1.0.safetensors` | 261,965,800 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\ltx-2-19b_vae.safetensors` | 2,445,014,077 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\ltx-2-19b_audio_vae.safetensors` | 106,537,820 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\ltx-2-19b_vocoder.safetensors` | 111,235,510 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\ltx-2-19b_text_embedding_projection.safetensors` | 1,445,096,790 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\ltx-2-19b-distilled_embeddings_connector.safetensors` | 1,417,919,090 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\gemma-3-12b-it-qat-q4_0-unquantized\gemma-3-12b-it-qat-q4_0-unquantized_quanto_bf16_int8.safetensors` | 13,210,647,730 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\gemma-3-12b-it-qat-q4_0-unquantized\tokenizer.json` | 33,384,570 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\gemma-3-12b-it-qat-q4_0-unquantized\tokenizer.model` | 4,689,074 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\gemma-3-12b-it-qat-q4_0-unquantized\tokenizer_config.json` | 1,157,001 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\gemma-3-12b-it-qat-q4_0-unquantized\added_tokens.json` | 35 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\gemma-3-12b-it-qat-q4_0-unquantized\chat_template.json` | 1,615 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\gemma-3-12b-it-qat-q4_0-unquantized\config_light.json` | 907 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\gemma-3-12b-it-qat-q4_0-unquantized\generation_config.json` | 173 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\gemma-3-12b-it-qat-q4_0-unquantized\preprocessor_config.json` | 570 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\gemma-3-12b-it-qat-q4_0-unquantized\processor_config.json` | 70 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\gemma-3-12b-it-qat-q4_0-unquantized\special_tokens_map.json` | 662 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\loras\ltx2\ltx-2-19b-ic-lora-union-control-ref0.5.safetensors` | 654,465,296 |

Total downloaded LTX-2 Q4 asset footprint:

- 33,339,671,904 bytes
- 31.05 GiB

## WanGP Settings Used

- Model family: `LTX-2`
- Model size: `2.0 19B`
- Variant: `Distilled GGUF Q4_K_M`
- Mode: text prompt only / text-to-video
- Audio: enabled through `Voices: Generate Video & Soundtrack based on Text Prompt`
- Resolution setting: `480x832 (9:16)`
- Output video stream resolution: `448x832`
- Frames: `121`
- Output duration: `5.041667s`
- FPS: `24`
- Inference steps: `8`
- Prompt audio strength: `1`
- Advanced mode: enabled

Prompt:

```text
Vertical smartphone UGC video, handheld phone camera, realistic beauty product demo. A woman sits at a clean vanity table and applies lipstick while looking into the phone camera. Natural bathroom lighting, casual authentic creator style, subtle hand movement, realistic facial expression, no mirror reflection, no text, no watermark. Include natural room tone, soft makeup sounds, lipstick cap click, subtle fabric movement, realistic ambient audio.
```

Note: WanGP accepted the `480x832` 9:16 resolution budget, and the encoded MP4 stream is `448x832`. This appears to be WanGP/LTX dimension adjustment while preserving the vertical format.

## Generation Result

- Generation completed: yes
- WanGP UI status: `Total Generation Time: 2m 38s`
- Output file: `C:\Users\USER\Documents\UGC_videos\Wan2GP\outputs\2026-05-14-14h26m42s_seed675518008_Vertical smartphone UGC video, handheld phone came.mp4`
- Output file size: 2,368,746 bytes
- Video stream: H.264, 448x832, 24 fps, 5.041667s
- Audio stream exists: yes
- Audio stream: AAC, mono, 24,000 Hz, 5.035000s

## VRAM And RAM Notes

- No VRAM out-of-memory error occurred.
- No RAM out-of-memory error occurred.
- Log line during LTX-2 load: `The whole model was pinned to reserved RAM: 51 large blocks spread across 12056.17 MB`
- Log line during LTX-2 load: `Async loading plan for model 'transformer' : base size of 443.19 MB will be preloaded with a 237.48 MB async circular shuttle`
- Log line during LTX-2 load: `Async loading plan for model 'text_encoder' : base size of 1920.48 MB will be preloaded with a 213.87 MB async circular shuttle`
- Observed GPU memory during generation polling: about 2,174 MiB used while denoising; 304 MiB after completion.
- Observed WanGP process memory after completion: about 33.18 GB working set.
- Warning: WanGP logged `[GGUF][llama.cpp CUDA] kernels unavailable, using fallback`. This did not block generation, but may affect GGUF performance.

## LTX-2.3 22B Q4_K_M Light Follow-Up

Date: 2026-05-14

Follow-up model:

`LTX-2 2.3 Distilled 1.0 GGUF Q4_K_M Light 22B`

Test queue:

`C:\Users\USER\Documents\UGC_videos\Wan2GP\test_queues\ltx23_q4_ugc_smoke.zip`

The first autoload attempt reached validation and queue processing, then stopped before model load because WanGP was running with `HF_HUB_OFFLINE` and the inherited `ltx2_22B_distilled` preload list expected three additional local files. These were downloaded manually:

| File | Bytes |
| --- | ---: |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\loras\ltx2\ltx-2.3-22b-ic-lora-outpaint.safetensors` | 1,308,756,416 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\loras\ltx2\ltx-2.3-22b-ic-lora-hdr-0.9.safetensors` | 327,309,312 |
| `C:\Users\USER\Documents\UGC_videos\Wan2GP\ckpts\ltx-2.3-22b-ic-lora-hdr-scene-emb.safetensors` | 12,583,096 |

The second autoload/render completed successfully.

- Output file: `C:\Users\USER\Documents\UGC_videos\Wan2GP\outputs\LTX23_Q4_UGC_Laptop_Test.mp4`
- Output file size: 4,182,140 bytes
- Video stream: H.264, 448x832, 24 fps, 241 frames, 10.041667s
- Audio stream exists: yes
- Audio stream: AAC, mono, 48,000 Hz, 10.026000s
- Log line during LTX-2.3 load: `The whole model was pinned to reserved RAM: 52 large blocks spread across 12390.27 MB`
- Log line during LTX-2.3 load: `Async loading plan for model 'transformer' : base size of 643.25 MB will be preloaded with a 269.48 MB async circular shuttle`
- Log line during LTX-2.3 load: `Async loading plan for model 'text_embeddings_connector' : 1923.52 MB will be preloaded (base size of 1.50 MB + 50.0% of recurrent layers data) with a 384.34 MB async shuttle`
- Observed GPU memory after completion: about 306 MiB used.
- Observed WanGP process memory after completion: about 35.77 GiB working set.
- Visual QA artifacts:
  - First frame extract: `C:\Users\USER\Documents\UGC_videos\Wan2GP\outputs\tests\ltx23_q4_ugc_first_frame.jpg`
  - Contact sheet: `C:\Users\USER\Documents\UGC_videos\Wan2GP\outputs\tests\ltx23_q4_ugc_contact_sheet.jpg`
  - The man and product remain visible, but the contact sheet shows a literal gold-frame/border artifact after the first frame. For a quality rerun, avoid the phrase `golden frame` in the prompt and refer to it as the `reference image` or `first image` instead.

## LTX-2.3 Wedding I2V Tests

Date: 2026-05-14

Test queue:

`C:\Users\USER\Documents\UGC_videos\Wan2GP\test_queues\ltx23_q4_wedding_combo_480p_720p.zip`

WanGP dry-run accepted both tasks. Because this is the distilled GGUF preset, WanGP reported locked `8` generation steps for both tasks, even though the queue carried the requested higher step values.

### Wedding Spin 480p

- Reference image: `C:\Users\USER\Documents\UGC_videos\Wan2GP\inputs\wedding_spin_reference_480x832.png`
- Queue setting: `480x832`, `121` frames, CFG `1.0`, NAG scale `2.0`, NAG tau `3.5`, NAG alpha `0.5`, start image strength `0.95`
- Output file: `C:\Users\USER\Documents\UGC_videos\Wan2GP\outputs\LTX23_Q4_Wedding_Spin_480p_Test.mp4`
- Output file size: 3,149,360 bytes
- Video stream: H.264, 448x832, 24 fps, 121 frames, 5.041667s
- Audio stream: AAC, mono, 48,000 Hz, 5.034000s
- Visual QA:
  - First frame extract: `C:\Users\USER\Documents\UGC_videos\Wan2GP\outputs\tests\wedding_spin_480p_first_frame.jpg`
  - Contact sheet: `C:\Users\USER\Documents\UGC_videos\Wan2GP\outputs\tests\wedding_spin_480p_contact_sheet.jpg`
  - The spin and bouquet-toward-lens action are visible. Because the source image cropped the upper face, the model hallucinates/reconstructs the full face during motion.

### Wedding Walk "I Do" 720p

- Reference image: `C:\Users\USER\Documents\UGC_videos\Wan2GP\inputs\wedding_walk_reference_736x1280.png`
- Queue setting: `736x1280`, `241` frames, CFG `1.0`, NAG scale `2.5`, NAG tau `3.5`, NAG alpha `0.5`, start image strength `0.90`
- Output file: `C:\Users\USER\Documents\UGC_videos\Wan2GP\outputs\LTX23_Q4_Wedding_Walk_IDo_720p_10s_Test.mp4`
- Output file size: 18,196,089 bytes
- Video stream: H.264, 704x1280, 24 fps, 241 frames, 10.041667s
- Audio stream: AAC, mono, 48,000 Hz, 10.026000s
- Visual QA:
  - First frame extract: `C:\Users\USER\Documents\UGC_videos\Wan2GP\outputs\tests\wedding_walk_ido_720p_first_frame.jpg`
  - Contact sheet: `C:\Users\USER\Documents\UGC_videos\Wan2GP\outputs\tests\wedding_walk_ido_720p_contact_sheet.jpg`
  - Identity, studio background, and dress detail stay consistent across the contact sheet. The arms extend gradually near the second half of the clip.

## Q6_K Recommendation

Q6_K is reasonable to test next, cautiously. The original 19B Q4_K_M run completed a 5-second generation with audio, and the LTX-2.3 22B Q4_K_M Light run completed a 10-second 241-frame generation with audio without VRAM or RAM errors.

Recommended next Q6_K test:

- Keep the same `480x832` setting.
- Start with `121` frames / about 5 seconds before trying another 241-frame run.
- Keep audio enabled.
- Download only `Distilled GGUF Q6_K`.
- Do not download Dev, Dev NVFP4, regular Distilled, or Q8_0.
