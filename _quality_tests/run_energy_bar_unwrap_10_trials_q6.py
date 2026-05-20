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
CONFIG_DIR = QUALITY_DIR / "energy_bar_unwrap_10_config"
CONFIG_PATH = CONFIG_DIR / "wgp_config.json"
START_FRAME = QUALITY_DIR / "kling_energy_bar_anchor_f000_wrapped.png"
EXPOSED_FRAME = QUALITY_DIR / "kling_energy_bar_anchor_f048_exposed.png"
FINAL_FRAME = QUALITY_DIR / "kling_energy_bar_anchor_f168_final.png"
RUN_LOG = QUALITY_DIR / "energy_bar_unwrap_10_trials_q6_running_log.md"
RESULTS_JSON = QUALITY_DIR / "energy_bar_unwrap_10_trials_q6_results.json"
RESULTS_CSV = QUALITY_DIR / "energy_bar_unwrap_10_trials_q6_tracker.csv"
FFMPEG = Path(sys.executable).parent / "Lib" / "site-packages" / "imageio_ffmpeg" / "binaries" / "ffmpeg-win-x86_64-v7.1.exe"


GLOBAL = (
    "Vertical 9:16 UGC selfie ad, photorealistic, same athletic man from the reference image, same dark workout outfit and headband, "
    "same blue wall, same soft window light from the left, same face, same body proportions, same skin tone. "
    "Medium selfie framing with face in upper half and product near his face, stable handheld smartphone camera, slight natural hand drift, no zoom, no dramatic camera movement, "
    "high identity consistency, best UGC realism, natural male fitness influencer delivery, clean lip sync, realistic hands, readable red energy bar wrapper."
)

STATE_MACHINE = (
    "Exact physical product state machine across the full 15 seconds: "
    "0 to 3 seconds, SEALED STATE: he smiles and holds one fully sealed red wrapped energy bar beside his face. "
    "3 to 6 seconds, TEAR STATE: both hands pinch the top seam and tear only the top edge of the wrapper open on camera. "
    "6 to 8 seconds, PEEL STATE: the red wrapper and white inner foil are peeled downward below the bite line, like a sleeve around the lower half of the bar. "
    "8 to 10.5 seconds, EXPOSED STATE: the top half is now a visible brown energy bar with oat and nut texture; the wrapper is only below it, not covering the bite area. "
    "10.5 to 12 seconds, BITE STATE: he takes one clear bite from the exposed brown bar only, never from the red wrapper. A bite mark appears in the exposed bar. "
    "12 to 15 seconds, END STATE: he chews, smiles, keeps the bitten exposed bar visible near his face, and says, \"Damn, that tastes good. Grab yours now.\""
)

WRAPPER_RULES = (
    "The wrapper must not regenerate after it is peeled down. Once the top half is exposed, the top half stays exposed until the end. "
    "The red wrapper remains below the bite line as a lower sleeve with a white foil flap hanging down. "
    "The exposed bar is a separate solid brown energy bar, not red wrapper, not melted wrapper, not a second wrapper. "
    "Hands, fingers, wrapper sleeve, white foil flap, and brown bar move together naturally as one held product."
)

NEGATIVE = (
    "black screen, blank video, bite wrapped bar, bite through wrapper, wrapper covering bite area after unwrapping, wrapper grows back, wrapper regenerates, "
    "red wrapper still on top of bar, skip unwrapping, sealed bar after peel, no exposed brown bar, unreadable product, product disappearing, duplicate bar, duplicate wrapper, "
    "changing wrapper design, changing person, changing outfit, changing background, identity drift, face morphing, distorted mouth, bad lip sync, frozen mouth, "
    "blurry face, waxy skin, extra fingers, warped hands, duplicate arms, heavy camera shake, cropped head, cropped product, zoom, dramatic camera, slow motion, object drift, bar floating"
)


TESTS = [
    (21, "baseline_state_machine_strength095", "S", [], 0.95, 5.0, STATE_MACHINE + " " + WRAPPER_RULES, "Pure text state-machine prompt, closest-current setting."),
    (22, "end_final_anchor_strength095", "SE", [FINAL_FRAME], 0.95, 5.0, STATE_MACHINE + " " + WRAPPER_RULES + " Final frame target: smiling man holding bitten exposed bar, red wrapper below the bite.", "End-image final bitten product anchor."),
    (23, "end_final_anchor_strength092", "SE", [FINAL_FRAME], 0.92, 5.0, STATE_MACHINE + " " + WRAPPER_RULES + " Final frame target: bitten exposed bar visible, wrapper below bite line.", "Slightly looser with final image anchor."),
    (24, "end_exposed_anchor_strength095", "SE", [EXPOSED_FRAME], 0.95, 5.0, STATE_MACHINE + " " + WRAPPER_RULES + " End-image anchor emphasizes the wrapper peeled down and the brown bar exposed; still include one bite before the end.", "End-image exposed-wrapper anchor."),
    (25, "peel_sleeve_language_strength093", "S", [], 0.93, 5.0, STATE_MACHINE + " The wrapper behaves like a loose sleeve: red sleeve below, white foil flap hanging, exposed brown bar above. Do not draw red wrapper over the bite area after peeling. " + WRAPPER_RULES, "Adds sleeve/flap language."),
    (26, "two_materials_brown_bar_red_wrapper_strength092", "S", [], 0.92, 5.0, STATE_MACHINE + " Distinguish two materials clearly: matte chewy brown food bar on top, glossy red wrapper sleeve on bottom, white foil flap between them. " + WRAPPER_RULES, "Explicit material separation."),
    (27, "slow_peel_no_bite_until_exposed_strength094", "S", [], 0.94, 5.0, STATE_MACHINE + " Slow the unwrapping down: no bite motion can begin until the brown bar is plainly visible for a full beat. He looks at the exposed bar before biting. " + WRAPPER_RULES, "Forces visible exposed beat before bite."),
    (28, "bite_mark_persistence_strength092", "SE", [FINAL_FRAME], 0.92, 5.0, STATE_MACHINE + " After the bite, preserve a visible crescent bite mark in the brown bar. The wrapper stays below the bite mark and never covers it. " + WRAPPER_RULES, "End anchor plus bite-mark persistence."),
    (29, "flow45_crisp_unwrap_strength093", "SE", [FINAL_FRAME], 0.93, 4.5, STATE_MACHINE + " Crisp efficient acting beats, no lingering. Tear, peel, show exposed bar, bite exposed bar, chew, speak. " + WRAPPER_RULES, "Flow 4.5 for crisper sequence."),
    (30, "polished_upload_unwrap_candidate", "SE", [FINAL_FRAME], 0.94, 4.5, STATE_MACHINE + " Polished uploadable UGC ad. The wrapper transition is clean and physically believable: sealed wrapper becomes lower sleeve, exposed brown bar gets bitten, final product remains visible. " + WRAPPER_RULES, "Best polish candidate."),
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


def make_settings(test: tuple) -> dict:
    index, variant, image_prompt_type, end_images, strength, flow_shift, prompt_tail, _note = test
    name = f"energy_bar_unwrap_t{index:02d}_q6_{variant}_seed_2705{index:02d}"
    return {
        "settings_version": 2.58,
        "model_type": "ltx2_22B_distilled_gguf_q6_k",
        "base_model_type": "ltx2_22B",
        "prompt": GLOBAL + " " + prompt_tail,
        "negative_prompt": NEGATIVE,
        "resolution": "512x896",
        "image_prompt_type": image_prompt_type,
        "image_start": [str(START_FRAME)],
        "image_end": [str(p) for p in end_images],
        "video_length": 361,
        "duration_seconds": 0.0,
        "force_fps": "24",
        "num_inference_steps": 8,
        "guidance_scale": 1.0,
        "guidance2_scale": 1.0,
        "guidance3_scale": 1.0,
        "audio_guidance_scale": 1.0,
        "audio_scale": 1.0,
        "flow_shift": flow_shift,
        "sliding_window_size": 481,
        "sliding_window_overlap": 17,
        "denoising_strength": 1.0,
        "masking_strength": 0,
        "input_video_strength": strength,
        "audio_prompt_type": "",
        "video_prompt_type": "",
        "guidance_phases": 2,
        "seed": int(f"2705{index:02d}"),
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
    for i in range(10):
        frame_no = round(i * (total - 1) / 9)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ok, frame = cap.read()
        if not ok:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        img.thumbnail((160, 284))
        tile = Image.new("RGB", (160, 304), "white")
        tile.paste(img, ((160 - img.width) // 2, 0))
        ImageDraw.Draw(tile).text((6, 286), f"f{frame_no}", fill=(0, 0, 0))
        thumbs.append(tile)
    cap.release()
    if not thumbs:
        return ""
    sheet = Image.new("RGB", (800, 608), "white")
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % 5) * 160, (i // 5) * 304))
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


def nvidia_snapshot() -> str:
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=temperature.gpu,power.draw,memory.used,memory.total,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            stderr=subprocess.STDOUT,
        )
        return out.strip()
    except Exception as exc:
        return f"nvidia-smi unavailable: {exc}"


def write_csv(results: list[dict]) -> None:
    fields = [
        "index",
        "variant",
        "status",
        "image_prompt_type",
        "end_image",
        "strength",
        "flow_shift",
        "seed",
        "duration",
        "elapsed_seconds",
        "black_screen_probe",
        "output_file",
        "windows_compatible_file",
        "contact_sheet",
        "settings_file",
        "note",
        "prompt",
    ]
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
                    "image_prompt_type": settings["image_prompt_type"],
                    "end_image": "; ".join(settings["image_end"]),
                    "strength": settings["input_video_strength"],
                    "flow_shift": settings["flow_shift"],
                    "seed": settings["seed"],
                    "duration": row.get("actual_duration_seconds", ""),
                    "elapsed_seconds": row.get("elapsed_seconds", ""),
                    "black_screen_probe": row.get("black_screen_probe", ""),
                    "output_file": row["generated_files"][0] if row["generated_files"] else "",
                    "windows_compatible_file": row.get("windows_compatible_file", ""),
                    "contact_sheet": row.get("contact_sheet", ""),
                    "settings_file": row["settings_file"],
                    "note": row["note"],
                    "prompt": settings["prompt"],
                }
            )


def main() -> int:
    for path in [START_FRAME, EXPOSED_FRAME, FINAL_FRAME]:
        if not path.exists():
            raise FileNotFoundError(path)
    prepare_config()
    RUN_LOG.write_text("# Energy Bar Unwrap 10-Trial Q6 Running Log\n\n", encoding="utf-8")
    append_log("Goal: keep current best UGC realism settings and improve wrapper state continuity.")
    append_log("Settings: Q6, 512x896, 361 frames, 24fps, flow 5.0/4.5, no LoRA, libx264_8 generation + Windows-compatible transcode.")
    append_log(f"Start frame: `{START_FRAME}`.")
    append_log(f"End anchors available: exposed=`{EXPOSED_FRAME}`, final=`{FINAL_FRAME}`.")
    append_log(f"Initial GPU snapshot: `{nvidia_snapshot()}`.")

    session = init(root=ROOT, config_path=CONFIG_PATH, output_dir=QUALITY_DIR, console_output=False, console_isatty=False)
    results = []
    for test in TESTS:
        index, variant, _ipt, _end, _strength, _flow, _prompt, note = test
        settings = make_settings(test)
        settings_path = QUALITY_DIR / f"{settings['output_filename']}.json"
        settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        append_log(f"Starting trial {index}: `{variant}`; image_prompt_type={settings['image_prompt_type']}; strength={settings['input_video_strength']}; flow={settings['flow_shift']}; GPU=`{nvidia_snapshot()}`.")
        started = time.perf_counter()
        row = {
            "index": index,
            "variant": variant,
            "note": note,
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
            f"Finished trial {index}: success={row['success']}; elapsed={row['elapsed_seconds']}s; "
            f"actual={row.get('actual_resolution', '')} {row.get('actual_fps', '')}fps/{row.get('actual_duration_seconds', '')}s; "
            f"black_probe={row.get('black_screen_probe', '')}; GPU=`{nvidia_snapshot()}`; "
            f"output=`{row['generated_files'][0] if row['generated_files'] else ''}`; wincompat=`{row.get('windows_compatible_file', '')}`."
        )
        if row["errors"]:
            append_log(f"Errors for trial {index}: `{'; '.join(row['errors'])}`.")
    append_log("Completed unwrap 10-trial run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
