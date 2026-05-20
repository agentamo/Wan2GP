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
CONFIG_DIR = QUALITY_DIR / "energy_bar_t11_7s_smoke_config"
CONFIG_PATH = CONFIG_DIR / "wgp_config.json"
SOURCE_SETTINGS = QUALITY_DIR / "energy_bar_ladder_t11_q6_15s_flow45_crisper_motion_seed_260511.json"
RUN_LOG = QUALITY_DIR / "energy_bar_t11_7s_smoke_q6_running_log.md"
RESULTS_JSON = QUALITY_DIR / "energy_bar_t11_7s_smoke_q6_results.json"
FFMPEG = Path(sys.executable).parent / "Lib" / "site-packages" / "imageio_ffmpeg" / "binaries" / "ffmpeg-win-x86_64-v7.1.exe"


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


def main() -> int:
    prepare_config()
    RUN_LOG.write_text("# Energy Bar T11 7s Smoke Q6 Running Log\n\n", encoding="utf-8")
    with SOURCE_SETTINGS.open("r", encoding="utf-8") as f:
        settings = json.load(f)
    settings["video_length"] = 169
    settings["output_filename"] = "energy_bar_t11_7s_smoke_q6_same_settings_seed_260511"
    settings_path = QUALITY_DIR / f"{settings['output_filename']}.json"
    settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    append_log(f"Prepared from `{SOURCE_SETTINGS.name}`; changed only video_length=169 and output filename.")

    session = init(root=ROOT, config_path=CONFIG_PATH, output_dir=QUALITY_DIR, console_output=False, console_isatty=False)
    started = time.perf_counter()
    row = {
        "settings_file": str(settings_path),
        "settings": settings,
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
            row["windows_compatible_file"] = transcode_wincompat(row["generated_files"][0])
            row["windows_compatible_probe"] = probe_video(row["windows_compatible_file"])
    except Exception as exc:
        row["errors"].append(str(exc))
    row["elapsed_seconds"] = round(time.perf_counter() - started, 1)
    RESULTS_JSON.write_text(json.dumps(row, indent=2), encoding="utf-8")
    append_log(
        f"Finished: success={row['success']}; elapsed={row['elapsed_seconds']}s; "
        f"actual={row.get('actual_resolution', '')} {row.get('actual_fps', '')}fps/{row.get('actual_duration_seconds', '')}s; "
        f"black_probe={row.get('black_screen_probe', '')}; output=`{row['generated_files'][0] if row['generated_files'] else ''}`; "
        f"wincompat=`{row.get('windows_compatible_file', '')}`."
    )
    if row["errors"]:
        append_log(f"Errors: `{'; '.join(row['errors'])}`.")
    return 0 if row["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
