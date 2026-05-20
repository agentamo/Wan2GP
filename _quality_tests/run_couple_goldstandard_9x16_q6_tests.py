from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.api import init


QUALITY_DIR = ROOT / "_quality_tests"
CONFIG_DIR = QUALITY_DIR / "goldstandard_9x16_config"
CONFIG_PATH = CONFIG_DIR / "wgp_config.json"
REFERENCE_IMAGE = ROOT / "ugcvideos" / "inputs" / "couple_red_studio_reference_20260505.png"
Kling_REFERENCE = QUALITY_DIR / "kling_20260514_Two_shot_v_3722_0.mp4"
BASELINE_REFERENCE = QUALITY_DIR / "couple_v3_t21_q6_crop9x16_30fps_crop_baseline_lock.mp4"
RUN_LOG = QUALITY_DIR / "couple_goldstandard_9x16_q6_running_log.md"
RESULTS_JSON = QUALITY_DIR / "couple_goldstandard_9x16_q6_results.json"
RESULTS_CSV = QUALITY_DIR / "couple_goldstandard_9x16_q6_tracker_source.csv"


BASE_PROMPT = (
    "Vertical 9:16 playful romantic couple image to video, same young couple from the reference image, "
    "bright red studio background, white formal outfits, natural body proportions, realistic body size, "
    "natural couple height difference, no stretched limbs, no oversized heads, both people visible in a natural "
    "medium portrait commercial frame, heads, shoulders, torsos, hands, red cans, and outfits visible. "
    "The girl playfully teases the man while holding the red cans from the reference image, the man smiles with an amused reaction. "
    "Natural affectionate movement, small believable torso movement, soft head turns, subtle shoulder motion, subtle hand movement, "
    "realistic micro-expressions, cute couple commercial style. Save the cheek kiss for the final third of the video; "
    "after the kiss she turns slightly toward the smartphone camera and says \"He'sss all mineee\" with playful elongated syllables, "
    "clear mouth shapes, readable lips, synced jaw and cheek movement, both smile at the end. Photorealistic, clean studio lighting, "
    "stable faces, identity consistency, smooth real human motion, real-time 30 fps smartphone commercial movement, natural speed human reactions, "
    "casual playful timing, normal human pacing, smooth continuous body motion, no slow motion."
)

CAN_LOCK = (
    " The red cans are locked in the girl's grip for the entire video, firmly held by her fingers and palms, "
    "same red cans from the reference image, cans stay physically attached to her hands, cans stay visible, cans keep the same scale and color, "
    "cans do not float, do not teleport, do not disappear, do not duplicate, do not melt into the hands. "
    "Hands, wrists, fingers, and cans move together as one connected rigid body; fingers wrap naturally around the cans with stable hand-object contact."
)

KLING_STYLE = (
    " Motion reference target: clean short-form ad realism like the Kling gold-standard clip, with crisp product lock, stable object scale, "
    "small expressive head and mouth movement, no drifting props, no puppet-like arm motion, and no theatrical slow cinematic timing."
)

NEGATIVE_PROMPT = (
    "slow motion, cinematic slow motion, frozen pose, held pose, stiff body, puppet motion, rubber arms, identity drift, changing face, "
    "different person, face morphing, distorted eyes, uneven eyes, broken mouth, unsynced mouth, frozen mouth, waxy skin, plastic skin, "
    "distorted hands, extra fingers, missing fingers, duplicated face, blurry face, red background changing, outfit changing, "
    "heavy cinematic lighting, floating cans, disappearing cans, duplicated cans, can teleporting, cans sliding out of hands, "
    "hands passing through cans, fused hands, fused fingers, melted cans, warped can labels, object drift, prop drift, "
    "unnatural body proportions, stretched body, tiny body, oversized head, cropped heads, cropped hands, cropped cans"
)


def append_log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with RUN_LOG.open("a", encoding="utf-8") as f:
        f.write(f"- `{timestamp}` {message}\n")


def prepare_config() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with (ROOT / "wgp_config.json").open("r", encoding="utf-8") as f:
        config = json.load(f)
    config["fit_canvas"] = 2
    config["last_resolution_choice"] = "512x896"
    config["video_output_codec"] = "libx264_10"
    config["video_container"] = "mp4"
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


VARIANTS = [
    {
        "index": 31,
        "variant": "native30_gold_prompt_lock",
        "suffix": CAN_LOCK + KLING_STYLE,
        "strength": 0.90,
        "seed": 240501,
        "fps": "30",
        "frames": 449,
        "temporal": "",
        "loras": [],
        "lora_mults": "",
        "note": "Direct continuation from t21 with Kling-style motion/product-lock language and high-quality x264 encode.",
    },
    {
        "index": 32,
        "variant": "native30_strong_ref_lock",
        "suffix": CAN_LOCK + " Prioritize the original reference pose, faces, can positions, and grip continuity over big movement." + KLING_STYLE,
        "strength": 0.95,
        "seed": 240501,
        "fps": "30",
        "frames": 449,
        "temporal": "",
        "loras": [],
        "lora_mults": "",
        "note": "Higher image reference strength for product/identity lock.",
    },
    {
        "index": 33,
        "variant": "native30_more_human_motion",
        "suffix": CAN_LOCK + " Allow a little more natural shoulder, head, and smile movement, but keep the cans locked to her hands." + KLING_STYLE,
        "strength": 0.85,
        "seed": 240501,
        "fps": "30",
        "frames": 449,
        "temporal": "",
        "loras": [],
        "lora_mults": "",
        "note": "Lower reference strength to test whether motion improves without prop drift.",
    },
    {
        "index": 34,
        "variant": "native30_lipsync_timing_clear",
        "suffix": CAN_LOCK
        + " Keep the first two thirds as playful teasing and smiling. In the final third, she kisses his cheek, turns toward camera, then speaks the line with clear visible syllables: Heee'sss all mineee. The mouth opens, narrows, and closes naturally for the words."
        + KLING_STYLE,
        "strength": 0.90,
        "seed": 240504,
        "fps": "30",
        "frames": 449,
        "temporal": "",
        "loras": [],
        "lora_mults": "",
        "note": "Uses the t19 lip-sync seed/timing idea while preserving the t21 portrait crop.",
    },
    {
        "index": 35,
        "variant": "native30_min_hand_travel",
        "suffix": CAN_LOCK
        + " Keep her hands near her cheeks and chest; use small playful teasing motion instead of wide arm travel. The cans remain readable and locked in her grip."
        + KLING_STYLE,
        "strength": 0.92,
        "seed": 240503,
        "fps": "30",
        "frames": 449,
        "temporal": "",
        "loras": [],
        "lora_mults": "",
        "note": "Minimizes hand travel to reduce can drift.",
    },
    {
        "index": 36,
        "variant": "rife30_15to30_gold_prompt",
        "suffix": CAN_LOCK + KLING_STYLE + " Generate natural 15 fps motion intended for smooth RIFE x2 interpolation to final 30 fps.",
        "strength": 0.90,
        "seed": 240501,
        "fps": "15",
        "frames": 225,
        "temporal": "rife2",
        "loras": [],
        "lora_mults": "",
        "note": "Tests WanGP RIFE x2 frame interpolation for smoother 30 fps final output.",
    },
    {
        "index": 37,
        "variant": "rife30_15to30_lipsync_clear",
        "suffix": CAN_LOCK
        + " The final spoken line has clean visible lip articulation and natural cheek movement before RIFE x2 interpolation to final 30 fps."
        + KLING_STYLE,
        "strength": 0.90,
        "seed": 240504,
        "fps": "15",
        "frames": 225,
        "temporal": "rife2",
        "loras": [],
        "lora_mults": "",
        "note": "Combines t19 lip timing with 15-to-30 RIFE interpolation.",
    },
    {
        "index": 38,
        "variant": "rife30_15to30_strong_ref_lock",
        "suffix": CAN_LOCK + " Keep identity and cans strongly anchored to the reference image while RIFE creates the in-between frames." + KLING_STYLE,
        "strength": 0.95,
        "seed": 240501,
        "fps": "15",
        "frames": 225,
        "temporal": "rife2",
        "loras": [],
        "lora_mults": "",
        "note": "RIFE interpolation plus stronger reference lock.",
    },
    {
        "index": 39,
        "variant": "native30_camera_micro_static",
        "suffix": CAN_LOCK
        + " Keep the camera mostly static like a locked smartphone tripod. No cinematic pan, no zoom, no dolly. Let only faces, shoulders, hands, and mouth move naturally."
        + KLING_STYLE,
        "strength": 0.90,
        "seed": 240505,
        "fps": "30",
        "frames": 449,
        "temporal": "",
        "loras": [],
        "lora_mults": "",
        "note": "Stabilizes camera so body and lips carry the realism.",
    },
    {
        "index": 40,
        "variant": "vbvr96000_guarded_short_memory_probe",
        "suffix": CAN_LOCK
        + " Use video reasoning to preserve consistent object contact and human movement. Keep motion small, believable, and commercially clean."
        + KLING_STYLE,
        "strength": 0.90,
        "seed": 240501,
        "fps": "30",
        "frames": 209,
        "temporal": "",
        "loras": ["Ltx2.3-Licon-VBVR-I2V-96000-R32.safetensors"],
        "lora_mults": "0.55",
        "note": "Guarded VBVR smoke probe only. Earlier Q6+VBVR failed on this laptop, so this is short and last.",
    },
]


def make_settings(variant: dict) -> dict:
    name = f"couple_v4_t{variant['index']:02d}_q6_gold9x16_{variant['variant']}_seed_{variant['seed']}"
    return {
        "settings_version": 2.58,
        "model_type": "ltx2_22B_distilled_gguf_q6_k",
        "base_model_type": "ltx2_22B",
        "prompt": BASE_PROMPT + variant["suffix"],
        "negative_prompt": NEGATIVE_PROMPT,
        "resolution": "512x896",
        "image_prompt_type": "S",
        "image_start": [str(REFERENCE_IMAGE)],
        "image_end": [],
        "video_length": variant["frames"],
        "duration_seconds": 0.0,
        "force_fps": variant["fps"],
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
        "input_video_strength": variant["strength"],
        "audio_prompt_type": "",
        "video_prompt_type": "",
        "guidance_phases": 2,
        "seed": variant["seed"],
        "batch_size": 1,
        "repeat_generation": 1,
        "activated_loras": variant["loras"],
        "loras_multipliers": variant["lora_mults"],
        "MMAudio_setting": 0,
        "temporal_upsampling": variant["temporal"],
        "spatial_upsampling": "",
        "override_profile": -1,
        "output_filename": name,
    }


def probe_video(path: str) -> dict:
    if not path:
        return {}
    data: dict[str, object] = {}
    try:
        import cv2

        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        data.update(
            {
                "actual_resolution": f"{width}x{height}",
                "actual_fps": round(float(fps), 3),
                "actual_frames": frames,
                "actual_duration_seconds": round(frames / fps, 2) if fps else "",
            }
        )
    except Exception as exc:
        data["probe_error"] = str(exc)

    file_path = Path(path)
    if file_path.exists():
        size_mb = round(file_path.stat().st_size / 1024 / 1024, 2)
        data["file_size_mb"] = size_mb
        duration = data.get("actual_duration_seconds")
        if isinstance(duration, (int, float)) and duration > 0:
            data["approx_total_bitrate_mbps"] = round((file_path.stat().st_size * 8) / duration / 1_000_000, 2)
    return data


def make_contact_sheet(video_path: str) -> str:
    if not video_path:
        return ""
    try:
        import cv2
        from PIL import Image, ImageDraw

        source = Path(video_path)
        out_path = source.with_name(source.stem + "_contact_sheet.jpg")
        cap = cv2.VideoCapture(str(source))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total <= 0:
            cap.release()
            return ""
        picks = [round(i * (total - 1) / 7) for i in range(8)]
        thumbs = []
        for frame_no in picks:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ok, frame = cap.read()
            if not ok:
                continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            img.thumbnail((180, 320))
            canvas = Image.new("RGB", (180, 340), "white")
            canvas.paste(img, ((180 - img.width) // 2, 0))
            draw = ImageDraw.Draw(canvas)
            draw.text((6, 322), f"f{frame_no}", fill=(0, 0, 0))
            thumbs.append(canvas)
        cap.release()
        if not thumbs:
            return ""
        sheet = Image.new("RGB", (180 * 4, 340 * 2), "white")
        for i, thumb in enumerate(thumbs):
            sheet.paste(thumb, ((i % 4) * 180, (i // 4) * 340))
        sheet.save(out_path, quality=92)
        return str(out_path)
    except Exception:
        return ""


def write_csv(results: list[dict]) -> None:
    fieldnames = [
        "test",
        "variant",
        "model",
        "requested_resolution",
        "actual_resolution",
        "requested_fps",
        "actual_fps",
        "requested_frames",
        "actual_frames",
        "duration_seconds",
        "seed",
        "input_video_strength",
        "fit_canvas",
        "codec",
        "temporal_upsampling",
        "lora_files",
        "lora_multipliers",
        "status",
        "elapsed_seconds",
        "file_size_mb",
        "approx_total_bitrate_mbps",
        "output_file",
        "file_link",
        "settings_file",
        "contact_sheet",
        "note",
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
                    "actual_resolution": result.get("actual_resolution", ""),
                    "requested_fps": settings["force_fps"],
                    "actual_fps": result.get("actual_fps", ""),
                    "requested_frames": settings["video_length"],
                    "actual_frames": result.get("actual_frames", ""),
                    "duration_seconds": result.get("actual_duration_seconds", ""),
                    "seed": settings["seed"],
                    "input_video_strength": settings["input_video_strength"],
                    "fit_canvas": 2,
                    "codec": "libx264_10",
                    "temporal_upsampling": settings["temporal_upsampling"],
                    "lora_files": "; ".join(settings["activated_loras"]),
                    "lora_multipliers": settings["loras_multipliers"],
                    "status": "success" if result["success"] else "failed",
                    "elapsed_seconds": result["elapsed_seconds"],
                    "file_size_mb": result.get("file_size_mb", ""),
                    "approx_total_bitrate_mbps": result.get("approx_total_bitrate_mbps", ""),
                    "output_file": output_file,
                    "file_link": output_file,
                    "settings_file": result["settings_file"],
                    "contact_sheet": result.get("contact_sheet", ""),
                    "note": result.get("note", ""),
                    "prompt": settings["prompt"],
                    "negative_prompt": settings["negative_prompt"],
                }
            )


def preflight() -> None:
    missing = [str(path) for path in [REFERENCE_IMAGE, BASELINE_REFERENCE, Kling_REFERENCE] if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required reference file(s): " + "; ".join(missing))


def main() -> int:
    QUALITY_DIR.mkdir(exist_ok=True)
    preflight()
    RUN_LOG.write_text("# Couple Gold Standard 9x16 Q6 Running Log\n\n", encoding="utf-8")
    prepare_config()
    append_log("Prepared temporary WanGP config: fit_canvas=2, last_resolution_choice=512x896, video_output_codec=libx264_10.")
    append_log(f"Baseline reference: `{BASELINE_REFERENCE}`.")
    append_log(f"Kling gold-standard reference: `{Kling_REFERENCE}`.")
    append_log("Research note: LTX 2.3 distilled settings are locked to 8 steps and CFG/guidance 1.0; res2s/HQ sampler is not available for distilled in this WanGP build.")
    append_log("Research note: official LTX 2.3 LipDub IC-LoRA is gated and requires a specific video+audio control pipeline, so it is not mixed into the Q6 baseline run.")

    tests = []
    for variant in VARIANTS:
        settings = make_settings(variant)
        settings_path = QUALITY_DIR / f"{settings['output_filename']}.json"
        with settings_path.open("w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        tests.append((variant, settings, settings_path))
        append_log(f"Wrote settings for test {variant['index']}: `{settings_path.name}`.")
        print(f"settings={settings_path}", flush=True)

    session = init(root=ROOT, config_path=CONFIG_PATH, output_dir=QUALITY_DIR, console_output=False, console_isatty=False)
    results = []

    for variant, settings, settings_path in tests:
        index = variant["index"]
        name = settings["output_filename"]
        append_log(f"Starting test {index}: `{name}`.")
        print(f"test_start={index} name={name}", flush=True)
        started = time.perf_counter()
        row = {
            "index": index,
            "variant": variant["variant"],
            "success": False,
            "elapsed_seconds": 0,
            "generated_files": [],
            "errors": [],
            "settings": settings,
            "settings_file": str(settings_path),
            "note": variant["note"],
        }
        try:
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
            row["success"] = result.success
            row["generated_files"] = [str(path) for path in result.generated_files]
            row["errors"] = [error.message for error in result.errors]
            probe = probe_video(row["generated_files"][0] if row["generated_files"] else "")
            row.update(probe)
            if row["generated_files"]:
                row["contact_sheet"] = make_contact_sheet(row["generated_files"][0])
        except Exception as exc:
            row["errors"] = [str(exc)]
        row["elapsed_seconds"] = round(time.perf_counter() - started, 1)

        print(f"test_done={index} name={name} elapsed_seconds={row['elapsed_seconds']} success={row['success']}", flush=True)
        for path in row["generated_files"]:
            print(f"generated={path}", flush=True)
        for error in row["errors"]:
            print(f"error={error}", flush=True)
        append_log(
            f"Finished test {index}: success={row['success']}, elapsed={row['elapsed_seconds']}s, "
            f"actual_resolution={row.get('actual_resolution', '')}, fps={row.get('actual_fps', '')}, "
            f"bitrate_mbps={row.get('approx_total_bitrate_mbps', '')}, output=`{row['generated_files'][0] if row['generated_files'] else ''}`."
        )
        if row["errors"]:
            append_log(f"Errors for test {index}: `{'; '.join(row['errors'])}`.")
        results.append(row)
        with RESULTS_JSON.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        write_csv(results)

    append_log("Completed batch and refreshed JSON/CSV tracker source.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
