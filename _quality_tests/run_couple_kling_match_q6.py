from __future__ import annotations

import json
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
CONFIG_DIR = QUALITY_DIR / "kling_match_config"
CONFIG_PATH = CONFIG_DIR / "wgp_config.json"
REFERENCE_IMAGE = ROOT / "ugcvideos" / "inputs" / "couple_red_studio_reference_20260505.png"
Kling_REFERENCE = QUALITY_DIR / "kling_20260514_Two_shot_v_3722_0.mp4"
RUN_LOG = QUALITY_DIR / "couple_kling_match_q6_running_log.md"
RESULTS_JSON = QUALITY_DIR / "couple_kling_match_q6_results.json"
FFMPEG = Path(sys.executable).parent / "Lib" / "site-packages" / "imageio_ffmpeg" / "binaries" / "ffmpeg-win-x86_64-v7.1.exe"


PROMPT = (
    "Seven second vertical smartphone commercial video, same young couple from the reference image, bright red studio background, "
    "white formal outfits, natural body proportions, realistic body size, stable faces, same identity, same hairstyles. "
    "Kling-style clean short-form ad realism: crisp product lock, stable object scale, small expressive head movement, natural mouth movement, "
    "smooth believable human reaction timing, no theatrical slow motion. "
    "Timeline: in seconds 0 to 2, the girl playfully presses the red cans near the man's cheek and he smiles with an amused reaction; "
    "seconds 2 to 4.8, she leans in and gives him one cute cheek kiss while both faces stay clear; "
    "seconds 4.8 to 7, she turns slightly toward the smartphone camera and says \"He'sss all mineee\" with clear readable lips, natural jaw and cheek movement, then both smile. "
    "The red cans are locked in the girl's grip for the entire video, firmly held by her fingers and palms, same cans from the reference image, "
    "hands, wrists, fingers, and cans move together as one connected rigid body; cans stay visible, same scale and color, no prop drift. "
    "Clean studio lighting, photorealistic skin texture, authentic playful couple ad, static smartphone camera, no zoom, no pan."
)

NEGATIVE_PROMPT = (
    "black screen, blank video, slow motion, cinematic slow motion, frozen pose, held pose, stiff body, puppet motion, rubber arms, identity drift, "
    "changing face, different person, face morphing, distorted eyes, uneven eyes, broken mouth, unsynced mouth, frozen mouth, waxy skin, plastic skin, "
    "distorted hands, extra fingers, missing fingers, duplicated face, blurry face, red background changing, outfit changing, heavy cinematic lighting, "
    "floating cans, disappearing cans, duplicated cans, can teleporting, cans sliding out of hands, hands passing through cans, fused hands, fused fingers, "
    "melted cans, warped can labels, object drift, prop drift, unnatural body proportions, stretched body, tiny body, oversized head, cropped heads, cropped hands, cropped cans"
)


TESTS = [
    {
        "index": 1,
        "name": "safe512_24fps_7s_kling_timing",
        "resolution": "512x896",
        "frames": 169,
        "fps": "24",
        "strength": 0.92,
        "seed": 26051501,
        "note": "First reverse-engineered Kling match: same 7.04s/24fps timing at laptop-safe portrait size.",
    },
    {
        "index": 2,
        "name": "safe512_24fps_7s_stronger_ref",
        "resolution": "512x896",
        "frames": 169,
        "fps": "24",
        "strength": 0.97,
        "seed": 26051501,
        "note": "Same as test 1 but stronger image reference for face/can lock.",
    },
    {
        "index": 3,
        "name": "safe512_30fps_7s_motion_compare",
        "resolution": "512x896",
        "frames": 209,
        "fps": "30",
        "strength": 0.92,
        "seed": 26051501,
        "note": "Compare native 30fps against Kling-matched 24fps while keeping the clip length about 7s.",
    },
]


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
    config["video_output_codec"] = "libx264_8"
    config["video_container"] = "mp4"
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def make_settings(test: dict) -> dict:
    output_name = f"couple_kling_match_t{test['index']:02d}_q6_{test['name']}_seed_{test['seed']}"
    return {
        "settings_version": 2.58,
        "model_type": "ltx2_22B_distilled_gguf_q6_k",
        "base_model_type": "ltx2_22B",
        "prompt": PROMPT,
        "negative_prompt": NEGATIVE_PROMPT,
        "resolution": test["resolution"],
        "image_prompt_type": "S",
        "image_start": [str(REFERENCE_IMAGE)],
        "image_end": [],
        "video_length": test["frames"],
        "duration_seconds": 0.0,
        "force_fps": test["fps"],
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
        "input_video_strength": test["strength"],
        "audio_prompt_type": "",
        "video_prompt_type": "",
        "guidance_phases": 2,
        "seed": test["seed"],
        "batch_size": 1,
        "repeat_generation": 1,
        "activated_loras": [],
        "loras_multipliers": "",
        "MMAudio_setting": 0,
        "temporal_upsampling": "",
        "spatial_upsampling": "",
        "override_profile": -1,
        "output_filename": output_name,
    }


def probe(path: str) -> dict:
    import cv2

    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    means = []
    for idx in [0, max(0, frames // 2), max(0, frames - 1)]:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        means.append(round(float(frame.mean()), 2) if ok and frame is not None else None)
    cap.release()
    p = Path(path)
    duration = round(frames / fps, 2) if fps else ""
    return {
        "actual_resolution": f"{width}x{height}",
        "actual_fps": round(float(fps), 3),
        "actual_frames": frames,
        "actual_duration_seconds": duration,
        "file_size_mb": round(p.stat().st_size / 1024 / 1024, 2),
        "approx_total_bitrate_mbps": round((p.stat().st_size * 8) / duration / 1_000_000, 2) if duration else "",
        "mean_brightness_samples": means,
        "black_screen_probe": all(v is not None and v < 5 for v in means),
    }


def transcode_wincompat(source: str, target_bitrate: str = "6500k") -> str:
    src = Path(source)
    out = src.with_name(src.stem + "_klingcodec_wincompat.mp4")
    cmd = [
        str(FFMPEG),
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(src),
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-c:v",
        "libx264",
        "-profile:v",
        "high",
        "-level",
        "4.1",
        "-pix_fmt",
        "yuv420p",
        "-tag:v",
        "avc1",
        "-b:v",
        target_bitrate,
        "-maxrate",
        target_bitrate,
        "-bufsize",
        "13000k",
        "-r",
        "24",
        "-fps_mode",
        "cfr",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-ar",
        "44100",
        "-ac",
        "2",
        "-movflags",
        "+faststart",
        str(out),
    ]
    subprocess.run(cmd, check=True)
    return str(out)


def main() -> int:
    QUALITY_DIR.mkdir(exist_ok=True)
    RUN_LOG.write_text("# Couple Kling-Match Q6 Running Log\n\n", encoding="utf-8")
    prepare_config()
    append_log("Target: Kling reference is 720x1280, 7.04s, 24fps, H.264 High avc1 yuv420p, AAC stereo, ~6.4 Mbps.")
    append_log("Approach: first match 7s timing/movement at 512x896; only move to 720x1280 after motion/identity are promising.")

    session = init(root=ROOT, config_path=CONFIG_PATH, output_dir=QUALITY_DIR, console_output=False, console_isatty=False)
    results = []
    for test in TESTS:
        settings = make_settings(test)
        settings_path = QUALITY_DIR / f"{settings['output_filename']}.json"
        settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        append_log(f"Starting test {test['index']}: `{settings['output_filename']}`.")
        started = time.perf_counter()
        row = {
            "index": test["index"],
            "name": test["name"],
            "note": test["note"],
            "settings": settings,
            "settings_file": str(settings_path),
            "success": False,
            "generated_files": [],
            "errors": [],
        }
        try:
            job = session.submit_task(settings)
            for event in job.events.iter(timeout=0.5):
                if event.kind == "progress":
                    progress = event.data
                    print(
                        f"progress={getattr(progress, 'progress', '')} "
                        f"step={getattr(progress, 'current_step', '')}/{getattr(progress, 'total_steps', '')} "
                        f"phase={getattr(progress, 'phase', '')}",
                        flush=True,
                    )
            result = job.result()
            row["success"] = result.success
            row["generated_files"] = [str(path) for path in result.generated_files]
            row["errors"] = [error.message for error in result.errors]
            if row["generated_files"]:
                row.update(probe(row["generated_files"][0]))
                compatible = transcode_wincompat(row["generated_files"][0])
                row["windows_compatible_file"] = compatible
                row["windows_compatible_probe"] = probe(compatible)
        except Exception as exc:
            row["errors"].append(str(exc))
        row["elapsed_seconds"] = round(time.perf_counter() - started, 1)
        results.append(row)
        RESULTS_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
        append_log(
            f"Finished test {test['index']}: success={row['success']}, elapsed={row['elapsed_seconds']}s, "
            f"actual={row.get('actual_resolution', '')} {row.get('actual_fps', '')}fps/{row.get('actual_duration_seconds', '')}s, "
            f"black_probe={row.get('black_screen_probe', '')}, output=`{row['generated_files'][0] if row['generated_files'] else ''}`, "
            f"wincompat=`{row.get('windows_compatible_file', '')}`."
        )
        if row["errors"]:
            append_log(f"Errors for test {test['index']}: `{'; '.join(row['errors'])}`.")
    append_log("Completed initial Kling-match ladder.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
