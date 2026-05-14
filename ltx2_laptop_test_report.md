# LTX-2 Laptop Q4 Smoke Test Report

Date: 2026-05-14
WanGP install: `C:\Users\USER\Documents\UGC_videos\Wan2GP`
WanGP version shown in UI: `v11.66`

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

## Q6_K Recommendation

Q6_K is safe to test next, cautiously, because Q4_K_M loaded, completed the 5-second generation, and produced an MP4 with audio without VRAM or RAM errors.

Recommended next Q6_K test:

- Keep the same `480x832` setting.
- Keep the same `121` frame 5-second duration.
- Keep audio enabled.
- Download only `Distilled GGUF Q6_K`.
- Do not download Dev, Dev NVFP4, regular Distilled, or Q8_0.
