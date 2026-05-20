from __future__ import annotations

import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.api import init


QUALITY_DIR = ROOT / "_quality_tests"
REFERENCE_IMAGE = ROOT / "ugcvideos" / "inputs" / "couple_red_studio_reference_20260505.png"
RUN_LOG = QUALITY_DIR / "couple_vertical_30fps_v2_running_log.md"
RESULTS_JSON = QUALITY_DIR / "couple_vertical_30fps_v2_results.json"
RESULTS_CSV = QUALITY_DIR / "couple_vertical_30fps_v2_tracker_source.csv"

BASE_PROMPT = (
    "Vertical 9:16 playful romantic couple image to video, same young couple from the reference image, "
    "bright red studio background, white formal outfits, natural body proportions, realistic body size, "
    "both people visible in a natural medium full-body commercial frame, no stretched limbs, no oversized heads, "
    "girl playfully teases the man while holding the red cans from the reference image, man smiles with amused reaction, "
    "natural affectionate movement, soft head turns, subtle hand movement, cute couple commercial style, "
    "final moment the girl kisses the man on the cheek, then turns slightly toward the camera and says \"He'sss all mineee,\" "
    "playful elongated syllables, both smile at the end, photorealistic, clean studio lighting, stable faces, "
    "identity consistency, smooth motion, real-time 30 fps smartphone commercial movement, natural speed human reactions, "
    "casual playful timing, normal human pacing, smooth continuous body motion, no slow motion."
)

CAN_LOCK = (
    " The red cans are locked in the girl's grip for the entire video, firmly held by her fingers and palms, "
    "same cans from the reference image, cans stay attached to her hands, cans stay visible, cans do not float, "
    "do not teleport, do not disappear, do not duplicate, do not melt into the hands, hands wrap naturally around the cans, "
    "stable hand-object contact, realistic grip pressure, fingers stay around the cans during teasing and smiling."
)

NEGATIVE_PROMPT = (
    "slow motion, cinematic slow motion, frozen pose, held pose, stiff body, identity drift, changing face, different person, "
    "face morphing, distorted eyes, uneven eyes, broken mouth, waxy skin, plastic skin, distorted hands, extra fingers, "
    "missing fingers, duplicated face, blurry face, red background changing, outfit changing, heavy cinematic lighting, "
    "floating cans, disappearing cans, duplicated cans, can teleporting, cans sliding out of hands, hands passing through cans, "
    "fused hands, fused fingers, melted cans, warped can labels, object drift, prop drift, unnatural body proportions, stretched body, "
    "tiny body, oversized head, cropped heads, cropped hands"
)


VARIANTS = [
    ("baseline_vertical_lock", CAN_LOCK, 0.90, 240501),
    ("stronger_grip_language", CAN_LOCK + " Her wrists and hands move together with the cans as one connected motion.", 0.90, 240501),
    ("more_static_cans", CAN_LOCK + " Keep the cans close to her cheeks and chest with only small playful movements.", 0.95, 240501),
    ("more_motion_but_locked", CAN_LOCK + " Allow gentle teasing movement but keep both cans continuously in contact with her hands.", 0.85, 240501),
    ("face_and_prop_lock", CAN_LOCK + " Same faces across every frame, same hairstyles, stable smiles, no identity drift for either person.", 0.90, 240501),
    ("composition_full_body", CAN_LOCK + " Vertical medium full-body framing, both outfits visible, natural couple height difference, realistic limb length.", 0.90, 240501),
    ("hands_visible", CAN_LOCK + " Keep both hands and both cans visible whenever possible, fingers clearly gripping the cans.", 0.90, 240502),
    ("less_hand_motion", CAN_LOCK + " Minimal hand travel, soft small movements, affectionate pose remains clear and stable.", 0.92, 240503),
    ("kiss_timing_clear", CAN_LOCK + " Save the cheek kiss for the final third of the video, then she faces camera for the spoken line.", 0.90, 240504),
    ("product_commercial_clean", CAN_LOCK + " Clean commercial product continuity, the cans remain the same size, color, and position relative to her hands.", 0.90, 240505),
]


def make_settings(index: int, variant_name: str, suffix: str, strength: float, seed: int) -> dict:
    name = f"couple_v2_t{index:02d}_q6_vertical30_{variant_name}_seed_{seed}"
    return {
        "settings_version": 2.58,
        "model_type": "ltx2_22B_distilled_gguf_q6_k",
        "base_model_type": "ltx2_22B",
        "prompt": BASE_PROMPT + suffix,
        "negative_prompt": NEGATIVE_PROMPT,
        "resolution": "480x832",
        "image_prompt_type": "S",
        "image_start": [str(REFERENCE_IMAGE)],
        "image_end": [],
        "video_length": 449,
        "duration_seconds": 0.0,
        "force_fps": "30",
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
        "input_video_strength": strength,
        "audio_prompt_type": "",
        "video_prompt_type": "",
        "guidance_phases": 2,
        "seed": seed,
        "batch_size": 1,
        "repeat_generation": 1,
        "activated_loras": [],
        "loras_multipliers": "",
        "MMAudio_setting": 0,
        "temporal_upsampling": "",
        "spatial_upsampling": "",
        "override_profile": -1,
        "output_filename": name,
    }


def append_log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with RUN_LOG.open("a", encoding="utf-8") as f:
        f.write(f"- `{timestamp}` {message}\n")


def write_csv(results: list[dict]) -> None:
    fieldnames = [
        "test",
        "variant",
        "model",
        "requested_resolution",
        "fps",
        "frames",
        "duration_target_seconds",
        "seed",
        "input_video_strength",
        "temporal_upsampling",
        "status",
        "elapsed_seconds",
        "output_file",
        "file_link",
        "prompt",
        "negative_prompt",
    ]
    with RESULTS_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            settings = result["settings"]
            output_file = result["generated_files"][0] if result["generated_files"] else ""
            writer.writerow(
                {
                    "test": result["index"],
                    "variant": result["variant"],
                    "model": settings["model_type"],
                    "requested_resolution": settings["resolution"],
                    "fps": settings["force_fps"],
                    "frames": settings["video_length"],
                    "duration_target_seconds": round(settings["video_length"] / int(settings["force_fps"]), 2),
                    "seed": settings["seed"],
                    "input_video_strength": settings["input_video_strength"],
                    "temporal_upsampling": settings["temporal_upsampling"] or "none",
                    "status": "success" if result["success"] else "failed",
                    "elapsed_seconds": result["elapsed_seconds"],
                    "output_file": output_file,
                    "file_link": output_file,
                    "prompt": settings["prompt"],
                    "negative_prompt": settings["negative_prompt"],
                }
            )


def main() -> int:
    QUALITY_DIR.mkdir(exist_ok=True)
    RUN_LOG.write_text("# Couple Vertical 30 FPS V2 Running Log\n\n", encoding="utf-8")
    append_log("Started Q6 vertical continuation batch from couple_t09 settings.")

    tests = []
    for offset, (variant_name, suffix, strength, seed) in enumerate(VARIANTS, start=11):
        settings = make_settings(offset, variant_name, suffix, strength, seed)
        settings_path = QUALITY_DIR / f"{settings['output_filename']}.json"
        with settings_path.open("w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        tests.append((variant_name, settings))
        append_log(f"Wrote settings for test {offset}: `{settings_path.name}`.")
        print(f"settings={settings_path}", flush=True)

    session = init(root=ROOT, output_dir=QUALITY_DIR, console_output=False, console_isatty=False)
    results = []

    for variant_name, settings in tests:
        index = int(settings["output_filename"].split("_t", 1)[1].split("_", 1)[0])
        name = settings["output_filename"]
        append_log(f"Starting test {index}: `{name}`.")
        print(f"test_start={index} name={name}", flush=True)
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
        elapsed = round(time.perf_counter() - started, 1)
        generated = [str(path) for path in result.generated_files]
        errors = [error.message for error in result.errors]
        print(f"test_done={index} name={name} elapsed_seconds={elapsed} success={result.success}", flush=True)
        for path in generated:
            print(f"generated={path}", flush=True)
        for error in errors:
            print(f"error={error}", flush=True)
        append_log(
            f"Finished test {index}: success={result.success}, elapsed={elapsed}s, "
            f"output=`{generated[0] if generated else ''}`."
        )
        results.append(
            {
                "index": index,
                "variant": variant_name,
                "success": result.success,
                "elapsed_seconds": elapsed,
                "generated_files": generated,
                "errors": errors,
                "settings": settings,
            }
        )
        with RESULTS_JSON.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        write_csv(results)

    append_log("Completed Q6 vertical continuation batch.")
    return 0 if all(item["success"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
