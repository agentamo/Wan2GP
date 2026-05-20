from __future__ import annotations

import csv
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
CONFIG_DIR = QUALITY_DIR / "energy_bar_stable_rollback_config"
CONFIG_PATH = CONFIG_DIR / "wgp_config.json"
REFERENCE_FRAME = QUALITY_DIR / "kling_energy_bar_first_frame.png"
RUN_LOG = QUALITY_DIR / "energy_bar_stable_rollback_2_q6_running_log.md"
RESULTS_JSON = QUALITY_DIR / "energy_bar_stable_rollback_2_q6_results.json"
RESULTS_CSV = QUALITY_DIR / "energy_bar_stable_rollback_2_q6_tracker.csv"
FFMPEG = Path(sys.executable).parent / "Lib" / "site-packages" / "imageio_ffmpeg" / "binaries" / "ffmpeg-win-x86_64-v7.1.exe"


BASE_PROMPT = (
    "Vertical 9:16 UGC selfie ad, photorealistic, same athletic man from the reference image, same dark workout outfit and headband, "
    "same red energy bar wrapper, same blue wall, same soft window light from the left, same face, same body proportions, same skin tone. "
    "Medium selfie framing with face in upper half and product near his face, stable handheld smartphone camera, slight natural hand drift, no zoom, no dramatic camera movement, "
    "high identity consistency, clean lip sync, natural male fitness influencer delivery, realistic hands, readable red wrapper. "
    "Exact 15 second action order: 0 to 3 seconds, he smiles at the camera and holds up the fully wrapped red energy bar beside his face; "
    "3 to 6 seconds, he uses both hands to tear open the top of the wrapper on camera; "
    "6 to 8 seconds, he pulls the wrapper down so the top half of the brown energy bar is visible; "
    "8 to 10.5 seconds, he raises the already unwrapped bar to his mouth and takes one clear bite from the exposed brown bar only; "
    "10.5 to 12.5 seconds, he chews naturally and reacts with a pleased smile; "
    "12.5 to 15 seconds, he looks into the lens and says, \"Damn, that tastes good. Grab yours now.\" "
    "Keep the partially unwrapped bar visible near his face while he speaks and end smiling with the bar held toward the camera. "
    "The product must remain visible throughout. The wrapper opens before the bite. Do not bite through the wrapper."
)

PROMPT_BAR_CLEAR = (
    BASE_PROMPT
    + " Make the food clearly read as a normal energy bar: brown chewy bar with oat and nut texture on the exposed top half, red wrapper below his fingers. "
    + "After the wrapper is pulled down, the exposed top remains brown food, not red wrapper."
)

PROMPT_BITE_CLEAR = (
    BASE_PROMPT
    + " The bite happens only after the brown energy bar is exposed. He bites the brown food portion once, leaves a visible bite mark, then keeps the bitten bar visible while speaking."
)

NEGATIVE_PROMPT = (
    "black screen, blank video, bite wrapped bar, bite through wrapper, skip unwrapping, no exposed brown bar, wrapper covering bite area, unreadable product, "
    "product disappearing, changing wrapper design, changing person, changing outfit, changing background, identity drift, face morphing, distorted mouth, bad lip sync, "
    "frozen mouth, blurry face, waxy skin, extra fingers, warped hands, duplicate arms, heavy camera shake, cropped head, cropped product, zoom, dramatic camera, slow motion, object drift"
)


TESTS = [
    {
        "index": 31,
        "variant": "rollback_t09_settings_bar_clear",
        "prompt": PROMPT_BAR_CLEAR,
        "strength": 0.92,
        "flow_shift": 5.0,
        "seed": 260509,
        "note": "Rollback to stable t09-style settings; only concise exposed-bar wording changed.",
    },
    {
        "index": 32,
        "variant": "rollback_t11_settings_bite_clear",
        "prompt": PROMPT_BITE_CLEAR,
        "strength": 0.92,
        "flow_shift": 4.5,
        "seed": 260511,
        "note": "Rollback to stable t11-style settings; concise bite-after-exposure wording.",
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
    name = f"energy_bar_stable_rollback_t{test['index']:02d}_q6_{test['variant']}_seed_{test['seed']}"
    return {
        "settings_version": 2.58,
        "model_type": "ltx2_22B_distilled_gguf_q6_k",
        "base_model_type": "ltx2_22B",
        "prompt": test["prompt"],
        "negative_prompt": NEGATIVE_PROMPT,
        "resolution": "512x896",
        "image_prompt_type": "S",
        "image_start": [str(REFERENCE_FRAME)],
        "image_end": [],
        "video_length": 361,
        "duration_seconds": 0.0,
        "force_fps": "24",
        "num_inference_steps": 8,
        "guidance_scale": 1.0,
        "guidance2_scale": 1.0,
        "guidance3_scale": 1.0,
        "audio_guidance_scale": 1.0,
        "audio_scale": 1.0,
        "flow_shift": test["flow_shift"],
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
        "output_filename": name,
    }


def probe_video(path: str) -> dict:
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


def make_contact_sheet(video_path: str) -> str:
    import cv2
    from PIL import Image, ImageDraw

    src = Path(video_path)
    out = src.with_name(src.stem + "_contact_sheet.jpg")
    cap = cv2.VideoCapture(str(src))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    thumbs = []
    for i in range(8):
        frame_no = round(i * (total - 1) / 7)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ok, frame = cap.read()
        if not ok:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        img.thumbnail((180, 320))
        tile = Image.new("RGB", (180, 340), "white")
        tile.paste(img, ((180 - img.width) // 2, 0))
        ImageDraw.Draw(tile).text((6, 322), f"f{frame_no}", fill=(0, 0, 0))
        thumbs.append(tile)
    cap.release()
    if not thumbs:
        return ""
    sheet = Image.new("RGB", (720, 680), "white")
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % 4) * 180, (i // 4) * 340))
    sheet.save(out, quality=92)
    return str(out)


def transcode_wincompat(source: str) -> str:
    src = Path(source)
    out = src.with_name(src.stem + "_wincompat.mp4")
    subprocess.run(
        [
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
            "6500k",
            "-maxrate",
            "6500k",
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
        ],
        check=True,
    )
    return str(out)


def write_csv(results: list[dict]) -> None:
    fields = ["index", "variant", "status", "strength", "flow_shift", "seed", "duration", "elapsed_seconds", "output_file", "windows_compatible_file", "contact_sheet", "settings_file", "note", "prompt"]
    with RESULTS_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in results:
            settings = row["settings"]
            writer.writerow(
                {
                    "index": row["index"],
                    "variant": row["variant"],
                    "status": "success" if row["success"] else "failed",
                    "strength": settings["input_video_strength"],
                    "flow_shift": settings["flow_shift"],
                    "seed": settings["seed"],
                    "duration": row.get("actual_duration_seconds", ""),
                    "elapsed_seconds": row.get("elapsed_seconds", ""),
                    "output_file": row["generated_files"][0] if row["generated_files"] else "",
                    "windows_compatible_file": row.get("windows_compatible_file", ""),
                    "contact_sheet": row.get("contact_sheet", ""),
                    "settings_file": row["settings_file"],
                    "note": row["note"],
                    "prompt": settings["prompt"],
                }
            )


def main() -> int:
    if not REFERENCE_FRAME.exists():
        raise FileNotFoundError(REFERENCE_FRAME)
    prepare_config()
    RUN_LOG.write_text("# Energy Bar Stable Rollback 2-Test Q6 Running Log\n\n", encoding="utf-8")
    append_log("Rollback after crash: using stable t08-t11 shape only. No SE/end-image guidance, no anchor images, no long state-machine prompt.")
    append_log("Settings: Q6, 512x896, 361 frames, 24fps, image_prompt_type=S, no LoRA, flow 5.0/4.5, libx264_8 + Windows transcode.")

    session = init(root=ROOT, config_path=CONFIG_PATH, output_dir=QUALITY_DIR, console_output=False, console_isatty=False)
    results = []
    for test in TESTS:
        settings = make_settings(test)
        settings_path = QUALITY_DIR / f"{settings['output_filename']}.json"
        settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        append_log(f"Starting rollback test {test['index']}: `{test['variant']}`; strength={test['strength']}; flow={test['flow_shift']}.")
        started = time.perf_counter()
        row = {
            "index": test["index"],
            "variant": test["variant"],
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
                row.update(probe_video(row["generated_files"][0]))
                row["contact_sheet"] = make_contact_sheet(row["generated_files"][0])
                row["windows_compatible_file"] = transcode_wincompat(row["generated_files"][0])
                row["windows_compatible_probe"] = probe_video(row["windows_compatible_file"])
        except Exception as exc:
            row["errors"].append(str(exc))
        row["elapsed_seconds"] = round(time.perf_counter() - started, 1)
        results.append(row)
        RESULTS_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
        write_csv(results)
        append_log(
            f"Finished rollback test {test['index']}: success={row['success']}; elapsed={row['elapsed_seconds']}s; "
            f"actual={row.get('actual_resolution', '')} {row.get('actual_fps', '')}fps/{row.get('actual_duration_seconds', '')}s; "
            f"black_probe={row.get('black_screen_probe', '')}; output=`{row['generated_files'][0] if row['generated_files'] else ''}`; "
            f"wincompat=`{row.get('windows_compatible_file', '')}`."
        )
        if row["errors"]:
            append_log(f"Errors for rollback test {test['index']}: `{'; '.join(row['errors'])}`.")
    append_log("Completed rollback 2-test run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
