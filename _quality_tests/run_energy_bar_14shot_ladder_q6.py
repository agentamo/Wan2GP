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
CONFIG_DIR = QUALITY_DIR / "energy_bar_14shot_ladder_config"
CONFIG_PATH = CONFIG_DIR / "wgp_config.json"
REFERENCE_FRAME = QUALITY_DIR / "kling_energy_bar_first_frame.png"
BEST_PRIOR = QUALITY_DIR / "energy_bar_kling_recreate_t01_q6_512x896_24fps_str_wincompat.mp4"
RUN_LOG = QUALITY_DIR / "energy_bar_14shot_ladder_q6_running_log.md"
RESULTS_JSON = QUALITY_DIR / "energy_bar_14shot_ladder_q6_results.json"
RESULTS_CSV = QUALITY_DIR / "energy_bar_14shot_ladder_q6_tracker.csv"
FFMPEG = Path(sys.executable).parent / "Lib" / "site-packages" / "imageio_ffmpeg" / "binaries" / "ffmpeg-win-x86_64-v7.1.exe"


GLOBAL_ANCHOR = (
    "Vertical 9:16 UGC selfie ad, photorealistic, same athletic man from the reference image, same dark workout outfit and headband, "
    "same red energy bar wrapper, same blue wall, same soft window light from the left, same face, same body proportions, same skin tone. "
    "Medium selfie framing with face in upper half and product near his face, stable handheld smartphone camera, slight natural hand drift, no zoom, no dramatic camera movement, "
    "high identity consistency, clean lip sync, natural male fitness influencer delivery, realistic hands, readable red wrapper."
)

FULL_15_ACTION = (
    "Exact 15 second action order: 0 to 3 seconds, he smiles at the camera and holds up the fully wrapped red energy bar beside his face; "
    "3 to 6 seconds, he uses both hands to clearly tear open the top of the wrapper on camera, with visible foil crinkle; "
    "6 to 8 seconds, he pulls the wrapper down so the top half of the bar is exposed, no bite yet; "
    "8 to 10.5 seconds, he raises the already unwrapped bar to his mouth and takes one clear bite from the exposed bar only; "
    "10.5 to 12.5 seconds, he chews naturally and reacts with a pleased smile; "
    "12.5 to 15 seconds, he looks into the lens and says, \"Damn, that tastes good. Grab yours now.\" "
    "Keep the partially unwrapped bar visible near his face while he speaks and end smiling with the bar held toward the camera."
)

PRODUCT_LOCK = (
    "The product must remain visible throughout. The hands, fingers, wrapper, and bar move together naturally. "
    "Do not skip the unwrapping step. Do not bite through the wrapper. The wrapper opens before the bite. "
    "Keep the wrapper design consistent and keep the exposed bar readable."
)

TEXTURE_PROOF = (
    "Show believable product texture when exposed: oats and nuts visible, chewy but solid, no melting, no crumbling mess. "
    "Use a tiny product-forward moment, not a full macro shot, so the man's face and identity stay stable."
)

NO_MESS_CTA = (
    "After the bite, he briefly shows clean fingertips near the wrapper, gives a quick approving nod, then finishes with the CTA line. "
    "Friendly high-energy fitness influencer tone, casual but clear."
)

NEGATIVE_PROMPT = (
    "black screen, blank video, bite wrapped bar, bite through wrapper, skip unwrapping, wrapper already gone too early, unreadable product, product disappearing, "
    "changing wrapper design, changing person, changing outfit, changing background, identity drift, face morphing, distorted mouth, bad lip sync, frozen mouth, "
    "blurry face, waxy skin, extra fingers, warped hands, duplicate arms, heavy camera shake, cropped head, cropped product, zoom, dramatic camera, "
    "slow motion, puppet motion, stiff hands, object drift, bar floating, wrapper fused to fingers"
)


TESTS = [
    (3, "7s_prior_rebuild_strength095", 169, "24", 0.95, 5.0, GLOBAL_ANCHOR + " " + FULL_15_ACTION.replace("15 second", "7 second condensed") + " " + PRODUCT_LOCK, "Rebuild closest t01 behavior as control."),
    (4, "7s_strength093_crisper_order", 169, "24", 0.93, 5.0, GLOBAL_ANCHOR + " " + FULL_15_ACTION.replace("15 second", "7 second condensed") + " " + PRODUCT_LOCK + " Emphasize clear action order over extra movement.", "Slightly lower strength, clearer action order."),
    (5, "7s_strength090_more_motion", 169, "24", 0.90, 5.0, GLOBAL_ANCHOR + " " + FULL_15_ACTION.replace("15 second", "7 second condensed") + " " + PRODUCT_LOCK, "Looser image lock for more unwrap/bite motion."),
    (6, "7s_texture_focus", 169, "24", 0.92, 5.0, GLOBAL_ANCHOR + " " + FULL_15_ACTION.replace("15 second", "7 second condensed") + " " + PRODUCT_LOCK + " " + TEXTURE_PROOF, "Adds texture proof language."),
    (7, "7s_nomess_cta_focus", 169, "24", 0.92, 5.0, GLOBAL_ANCHOR + " " + FULL_15_ACTION.replace("15 second", "7 second condensed") + " " + PRODUCT_LOCK + " " + NO_MESS_CTA, "Adds no-mess and CTA behavior."),
    (8, "15s_strength095_full_order", 361, "24", 0.95, 5.0, GLOBAL_ANCHOR + " " + FULL_15_ACTION + " " + PRODUCT_LOCK, "First full 15s candidate, strongest identity/product lock."),
    (9, "15s_strength092_balanced", 361, "24", 0.92, 5.0, GLOBAL_ANCHOR + " " + FULL_15_ACTION + " " + PRODUCT_LOCK, "Balanced 15s candidate."),
    (10, "15s_strength090_motion", 361, "24", 0.90, 5.0, GLOBAL_ANCHOR + " " + FULL_15_ACTION + " " + PRODUCT_LOCK, "More motion freedom."),
    (11, "15s_flow45_crisper_motion", 361, "24", 0.92, 4.5, GLOBAL_ANCHOR + " " + FULL_15_ACTION + " " + PRODUCT_LOCK + " Crisp efficient acting beats, no lingering pauses.", "Flow shift 4.5."),
    (12, "15s_flow55_stability", 361, "24", 0.92, 5.5, GLOBAL_ANCHOR + " " + FULL_15_ACTION + " " + PRODUCT_LOCK + " Stable face and product continuity are more important than big gestures.", "Flow shift 5.5."),
    (13, "15s_texture_nomess_cta", 361, "24", 0.92, 5.0, GLOBAL_ANCHOR + " " + FULL_15_ACTION + " " + PRODUCT_LOCK + " " + TEXTURE_PROOF + " " + NO_MESS_CTA, "Full product proof + CTA."),
    (14, "15s_polished_upload_candidate", 361, "24", 0.93, 5.0, GLOBAL_ANCHOR + " " + FULL_15_ACTION + " " + PRODUCT_LOCK + " " + TEXTURE_PROOF + " " + NO_MESS_CTA + " Polished uploadable UGC ad, realistic pacing, no artifacts, clear face, clear product, clean ending smile.", "Main polished candidate."),
    (15, "15s_highlock_upload_alt", 361, "24", 0.96, 5.0, GLOBAL_ANCHOR + " " + FULL_15_ACTION + " " + PRODUCT_LOCK + " " + NO_MESS_CTA + " Prioritize identity and product lock even if movement is slightly smaller.", "High-lock upload alternate."),
    (16, "15s_motion_upload_alt", 361, "24", 0.89, 5.0, GLOBAL_ANCHOR + " " + FULL_15_ACTION + " " + PRODUCT_LOCK + " " + TEXTURE_PROOF + " Natural human movement and believable hand physics, but keep product visible and identity stable.", "Motion-focused upload alternate."),
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
    index, variant, frames, fps, strength, flow_shift, prompt, _note = test
    name = f"energy_bar_ladder_t{index:02d}_q6_{variant}_seed_2605{index:02d}"
    return {
        "settings_version": 2.58,
        "model_type": "ltx2_22B_distilled_gguf_q6_k",
        "base_model_type": "ltx2_22B",
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "resolution": "512x896",
        "image_prompt_type": "S",
        "image_start": [str(REFERENCE_FRAME)],
        "image_end": [],
        "video_length": frames,
        "duration_seconds": 0.0,
        "force_fps": fps,
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
        "seed": int(f"2605{index:02d}"),
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
    fields = [
        "index",
        "variant",
        "status",
        "frames",
        "fps",
        "duration",
        "strength",
        "flow_shift",
        "seed",
        "elapsed_seconds",
        "black_screen_probe",
        "bitrate_mbps",
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
                    "frames": settings["video_length"],
                    "fps": settings["force_fps"],
                    "duration": row.get("actual_duration_seconds", ""),
                    "strength": settings["input_video_strength"],
                    "flow_shift": settings["flow_shift"],
                    "seed": settings["seed"],
                    "elapsed_seconds": row.get("elapsed_seconds", ""),
                    "black_screen_probe": row.get("black_screen_probe", ""),
                    "bitrate_mbps": row.get("approx_total_bitrate_mbps", ""),
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
    RUN_LOG.write_text("# Energy Bar 14-Shot Q6 Ladder Running Log\n\n", encoding="utf-8")
    append_log(f"Prior closest representation: `{BEST_PRIOR}`.")
    append_log("WanGP-only ladder. No ComfyUI prompt relay. Final goal: polished 15s uploadable UGC clip.")
    append_log("Settings baseline: Q6, 512x896, 24fps, fit_canvas=2, libx264_8 generation plus Windows-compatible transcode.")

    session = init(root=ROOT, config_path=CONFIG_PATH, output_dir=QUALITY_DIR, console_output=False, console_isatty=False)
    results = []
    for test in TESTS:
        index, variant, _frames, _fps, _strength, _flow_shift, _prompt, note = test
        settings = make_settings(test)
        settings_path = QUALITY_DIR / f"{settings['output_filename']}.json"
        settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        append_log(f"Starting shot/test {index}: `{variant}`; strength={settings['input_video_strength']}, flow_shift={settings['flow_shift']}, frames={settings['video_length']}.")
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
            f"Finished shot/test {index}: success={row['success']}, elapsed={row['elapsed_seconds']}s, "
            f"actual={row.get('actual_resolution', '')} {row.get('actual_fps', '')}fps/{row.get('actual_duration_seconds', '')}s, "
            f"black_probe={row.get('black_screen_probe', '')}, output=`{row['generated_files'][0] if row['generated_files'] else ''}`, "
            f"wincompat=`{row.get('windows_compatible_file', '')}`."
        )
        if row["errors"]:
            append_log(f"Errors for shot/test {index}: `{'; '.join(row['errors'])}`.")
    append_log("Completed 14-shot ladder.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
