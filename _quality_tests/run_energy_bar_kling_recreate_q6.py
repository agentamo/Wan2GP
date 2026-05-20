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
CONFIG_DIR = QUALITY_DIR / "energy_bar_kling_recreate_config"
CONFIG_PATH = CONFIG_DIR / "wgp_config.json"
REFERENCE_FRAME = QUALITY_DIR / "kling_energy_bar_first_frame.png"
SOURCE_VIDEO = QUALITY_DIR / "kling_20260514_Two_shot_v_3722_0.mp4"
RUN_LOG = QUALITY_DIR / "energy_bar_kling_recreate_q6_running_log.md"
RESULTS_JSON = QUALITY_DIR / "energy_bar_kling_recreate_q6_results.json"
FFMPEG = Path(sys.executable).parent / "Lib" / "site-packages" / "imageio_ffmpeg" / "binaries" / "ffmpeg-win-x86_64-v7.1.exe"


PROMPT = (
    "Two-shot vertical UGC selfie ad, photorealistic, natural smartphone camera, same man, same outfit, same red energy bar, "
    "same blue wall, same soft window light, same face, same body proportions. Keep strong identity consistency across both shots. "
    "Medium selfie framing, stable handheld phone camera, slight natural hand drift, no zoom, no dramatic camera movement."
    "Shot 1, 0.0 to 3.5 seconds: He smiles at the camera and holds up the fully wrapped energy bar beside his face. "
    "Then he uses both hands to clearly tear open the top of the wrapper on camera. Show the wrapper opening clearly. "
    "Then he pulls the wrapper down so the top half of the bar is visibly exposed. He does not bite yet. "
    "End shot 1 with the bar clearly unwrapped and exposed in his hand."
    "Shot 2, 3.5 to 7.0 seconds: Same man, same framing, same setting. He raises the already unwrapped bar to his mouth "
    "and takes one clear bite from the exposed bar only. He chews naturally, reacts with a pleased smile, then looks into the lens "
    "and says, \"Damn, that tastes good.\" Keep the partially unwrapped bar visible near his face while he speaks. "
    "End with him smiling and holding the bar toward the camera."
    "Audio: natural male voice, friendly fitness influencer tone, casual UGC delivery, clear speech, accurate lip sync, "
    "short natural chewing pause before the spoken line, light room tone."
    "Important constraints: action must happen in this exact order, hold wrapped bar, tear wrapper open, expose bar, bite exposed bar, "
    "chew, then speak. Do not skip the unwrapping step. Do not bite through the wrapper. Keep the product visible throughout. "
    "Keep hand motion natural and realistic."
)

NEGATIVE_PROMPT = (
    "do not bite the wrapped bar, do not skip the unwrapping step, no blurry face, no distorted mouth, no bad lip sync, "
    "no extra fingers, no warped hands, no changing wrapper design, no unreadable product, no morphing, no duplicate arms, "
    "no heavy camera shake, no cropped head, no cropped product, no different person, no different outfit, no different background, "
    "black screen, blank video"
)


TESTS = [
    {
        "index": 1,
        "variant": "q6_512x896_24fps_strength095",
        "resolution": "512x896",
        "frames": 169,
        "fps": "24",
        "strength": 0.95,
        "seed": 26051511,
        "note": "First recreation from Kling first frame, laptop-safe size, same 7.04s/24fps timing.",
    },
    {
        "index": 2,
        "variant": "q6_512x896_24fps_strength090",
        "resolution": "512x896",
        "frames": 169,
        "fps": "24",
        "strength": 0.90,
        "seed": 26051512,
        "note": "Slightly looser image lock to allow more unwrapping/biting motion.",
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
    output_name = f"energy_bar_kling_recreate_t{test['index']:02d}_{test['variant']}_seed_{test['seed']}"
    return {
        "settings_version": 2.58,
        "model_type": "ltx2_22B_distilled_gguf_q6_k",
        "base_model_type": "ltx2_22B",
        "prompt": PROMPT,
        "negative_prompt": NEGATIVE_PROMPT,
        "resolution": test["resolution"],
        "image_prompt_type": "S",
        "image_start": [str(REFERENCE_FRAME)],
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

    source = Path(video_path)
    out_path = source.with_name(source.stem + "_contact_sheet.jpg")
    cap = cv2.VideoCapture(str(source))
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
    sheet.save(out_path, quality=92)
    return str(out_path)


def transcode_kling_codec(source: str) -> str:
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


def main() -> int:
    if not SOURCE_VIDEO.exists():
        raise FileNotFoundError(SOURCE_VIDEO)
    if not REFERENCE_FRAME.exists():
        raise FileNotFoundError(REFERENCE_FRAME)
    prepare_config()
    RUN_LOG.write_text("# Energy Bar Kling Recreate Q6 Running Log\n\n", encoding="utf-8")
    append_log(f"Source video: `{SOURCE_VIDEO}`.")
    append_log(f"First-frame start image: `{REFERENCE_FRAME}`.")
    append_log("Target spec: 7.04 seconds, 24 fps, vertical, Windows-compatible H.264 High avc1 yuv420p/AAC copy.")

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
                row["windows_compatible_file"] = transcode_kling_codec(row["generated_files"][0])
                row["windows_compatible_probe"] = probe_video(row["windows_compatible_file"])
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
