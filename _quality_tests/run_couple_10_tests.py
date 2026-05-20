from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.api import init


QUALITY_DIR = ROOT / "_quality_tests"
REFERENCE_IMAGE = Path(r"C:\Users\USER\Pictures\Screenshots\Screenshot 2026-05-05 011837.png")
LOCAL_REFERENCE_IMAGE = ROOT / "ugcvideos" / "inputs" / "couple_red_studio_reference_20260505.png"

BASE_PROMPT = (
    "Playful romantic couple image to video, same young couple from the reference image, "
    "bright red studio background, white formal outfits, girl playfully teases the man, "
    "man smiles with amused reaction, natural affectionate movement, soft head turns, "
    "subtle hand movement, cute couple commercial style, final moment the girl kisses the man "
    "on the cheek, then turns slightly toward the camera and says \"He'sss all mineee,\" "
    "playful elongated syllables, both smile at the end, photorealistic, clean studio lighting, "
    "stable faces, identity consistency, smooth motion."
)

REALTIME_PROMPT_SUFFIX = (
    " Real-time 30 fps smartphone commercial movement, natural speed human reactions, "
    "casual playful timing, normal human pacing, smooth continuous body motion, no slow motion."
)

FACE_LOCK_PROMPT_SUFFIX = (
    " Same faces for both people across every frame, same eye shape, same nose, same mouth, "
    "same hairstyle, no identity drift, no face swapping, no age change."
)

NEGATIVE_PROMPT = (
    "slow motion, cinematic slow motion, frozen pose, held pose, stiff body, identity drift, "
    "changing face, different person, face morphing, distorted eyes, uneven eyes, broken mouth, "
    "waxy skin, plastic skin, distorted hands, extra fingers, missing fingers, duplicated face, "
    "blurry face, product disappearing, red background changing, outfit changing, heavy cinematic lighting"
)


def make_settings(
    name: str,
    model_type: str,
    prompt: str,
    seed: int,
    force_fps: str,
    frames: int,
    input_strength: float,
    temporal_upsampling: str = "",
) -> dict:
    return {
        "settings_version": 2.58,
        "model_type": model_type,
        "base_model_type": "ltx2_22B",
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "resolution": "640x480",
        "image_prompt_type": "S",
        "image_start": [str(LOCAL_REFERENCE_IMAGE)],
        "image_end": [],
        "video_length": frames,
        "duration_seconds": 0.0,
        "force_fps": force_fps,
        "num_inference_steps": 8,
        "guidance_scale": 1.0,
        "guidance2_scale": 1.0,
        "guidance3_scale": 1.0,
        "audio_guidance_scale": 1.0,
        "audio_scale": 1.0,
        "flow_shift": 5.0,
        "sliding_window_size": 481,
        "sliding_window_overlap": 17,
        "denoising_strength": 1.0,
        "masking_strength": 0,
        "input_video_strength": input_strength,
        "audio_prompt_type": "",
        "video_prompt_type": "",
        "guidance_phases": 2,
        "seed": seed,
        "batch_size": 1,
        "repeat_generation": 1,
        "activated_loras": [],
        "loras_multipliers": "",
        "MMAudio_setting": 0,
        "temporal_upsampling": temporal_upsampling,
        "spatial_upsampling": "",
        "override_profile": -1,
        "output_filename": name,
    }


def main() -> int:
    QUALITY_DIR.mkdir(exist_ok=True)
    LOCAL_REFERENCE_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REFERENCE_IMAGE, LOCAL_REFERENCE_IMAGE)

    q6 = "ltx2_22B_distilled_gguf_q6_k"
    q4 = "ltx2_22B_distilled_gguf_q4_k_m"
    prompt_realtime = BASE_PROMPT + REALTIME_PROMPT_SUFFIX
    prompt_realtime_face = BASE_PROMPT + REALTIME_PROMPT_SUFFIX + FACE_LOCK_PROMPT_SUFFIX

    tests = [
        make_settings("couple_t01_q4_30fps_native_strength100_seed_240501", q4, BASE_PROMPT, 240501, "30", 449, 1.0),
        make_settings("couple_t02_q4_30fps_native_strength090_seed_240501", q4, BASE_PROMPT, 240501, "30", 449, 0.9),
        make_settings("couple_t03_q4_30fps_native_strength080_seed_240501", q4, BASE_PROMPT, 240501, "30", 449, 0.8),
        make_settings("couple_t04_q4_30fps_realtime_strength090_seed_240501", q4, prompt_realtime, 240501, "30", 449, 0.9),
        make_settings("couple_t05_q4_30fps_facelock_strength090_seed_240501", q4, prompt_realtime_face, 240501, "30", 449, 0.9),
        make_settings("couple_t06_q4_rife2_15to30_strength090_seed_240501", q4, prompt_realtime, 240501, "15", 225, 0.9, "rife2"),
        make_settings("couple_t07_q6_30fps_native_strength100_seed_240501", q6, BASE_PROMPT, 240501, "30", 449, 1.0),
        make_settings("couple_t08_q6_30fps_native_strength090_seed_240501", q6, BASE_PROMPT, 240501, "30", 449, 0.9),
        make_settings("couple_t09_q6_30fps_realtime_strength090_seed_240501", q6, prompt_realtime, 240501, "30", 449, 0.9),
        make_settings("couple_t10_q6_rife2_15to30_strength090_seed_240501", q6, prompt_realtime, 240501, "15", 225, 0.9, "rife2"),
    ]

    for index, settings in enumerate(tests, start=1):
        settings_path = QUALITY_DIR / f"{settings['output_filename']}.json"
        with settings_path.open("w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        print(f"settings={settings_path}", flush=True)

    session = init(root=ROOT, output_dir=QUALITY_DIR, console_output=False, console_isatty=False)
    results = []

    for index, settings in enumerate(tests, start=1):
        name = settings["output_filename"]
        print(f"test_start={index}/10 name={name}", flush=True)
        started = time.perf_counter()
        job = session.submit_task(settings)
        for event in job.events.iter(timeout=0.5):
            if event.kind == "progress":
                progress = event.data
                print(
                    "progress="
                    f"{getattr(progress, 'progress', '')} "
                    f"step={getattr(progress, 'current_step', '')}/{getattr(progress, 'total_steps', '')} "
                    f"phase={getattr(progress, 'phase', '')}",
                    flush=True,
                )
        result = job.result()
        elapsed = time.perf_counter() - started
        generated = [str(path) for path in result.generated_files]
        errors = [error.message for error in result.errors]
        print(f"test_done={index}/10 name={name} elapsed_seconds={elapsed:.1f} success={result.success}", flush=True)
        for path in generated:
            print(f"generated={path}", flush=True)
        for error in errors:
            print(f"error={error}", flush=True)
        results.append(
            {
                "index": index,
                "name": name,
                "success": result.success,
                "elapsed_seconds": round(elapsed, 1),
                "generated_files": generated,
                "errors": errors,
                "settings": settings,
            }
        )
        with (QUALITY_DIR / "couple_10_tests_results.json").open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    return 0 if all(item["success"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
