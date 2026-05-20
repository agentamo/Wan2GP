from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUALITY_DIR = ROOT / "_quality_tests"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(QUALITY_DIR) not in sys.path:
    sys.path.insert(0, str(QUALITY_DIR))

from shared.api import init
from run_couple_goldstandard_9x16_q6_tests import (
    CAN_LOCK,
    CONFIG_PATH,
    KLING_STYLE,
    RESULTS_JSON,
    append_log,
    make_contact_sheet,
    make_settings,
    prepare_config,
    probe_video,
    write_csv,
)


CONTINUATION_VARIANTS = [
    {
        "index": 41,
        "variant": "native30_t19_lip_sync_refined",
        "suffix": CAN_LOCK
        + " Use the best lip-sync timing from the earlier t19 test: the cheek kiss happens late, then she faces the camera and clearly forms the words Heee'sss all mineee with natural jaw, cheek, and lip motion."
        + KLING_STYLE,
        "strength": 0.90,
        "seed": 240504,
        "fps": "30",
        "frames": 449,
        "temporal": "",
        "loras": [],
        "lora_mults": "",
        "note": "Native 30 fps continuation using the t19 lip-sync seed/timing idea, no RIFE.",
    },
    {
        "index": 42,
        "variant": "native30_high_ref_prop_lock",
        "suffix": CAN_LOCK
        + " Prioritize exact grip continuity and original can placement. The cans remain locked to the same fingers throughout teasing, smiling, kissing, and speaking."
        + KLING_STYLE,
        "strength": 0.97,
        "seed": 240510,
        "fps": "30",
        "frames": 449,
        "temporal": "",
        "loras": [],
        "lora_mults": "",
        "note": "Highest reference-strength native 30 test for can lock and identity preservation.",
    },
    {
        "index": 43,
        "variant": "native30_natural_reaction_microexpressions",
        "suffix": CAN_LOCK
        + " Add believable tiny reaction timing: he smiles wider after the tease, she smiles before the kiss, shoulders and eyes react softly, with no big camera movement."
        + KLING_STYLE,
        "strength": 0.88,
        "seed": 240511,
        "fps": "30",
        "frames": 449,
        "temporal": "",
        "loras": [],
        "lora_mults": "",
        "note": "Slightly looser reference strength to chase more natural human reaction movement.",
    },
    {
        "index": 44,
        "variant": "native30_static_camera_product_readable",
        "suffix": CAN_LOCK
        + " Keep the camera locked like a tripod smartphone ad, keep the red background clean, keep both faces and the cans readable, and avoid cinematic pan or zoom."
        + KLING_STYLE,
        "strength": 0.93,
        "seed": 240512,
        "fps": "30",
        "frames": 449,
        "temporal": "",
        "loras": [],
        "lora_mults": "",
        "note": "Static-camera product-readable native 30 fps test.",
    },
]


def load_existing_results() -> list[dict]:
    if not RESULTS_JSON.exists():
        return []
    with RESULTS_JSON.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def main() -> int:
    prepare_config()
    append_log("Continuation: previous run stopped after t36; t37-t40 were not completed. Running four native-30 Q6 continuation tests t41-t44.")
    session = init(root=ROOT, config_path=CONFIG_PATH, output_dir=QUALITY_DIR, console_output=False, console_isatty=False)
    results = load_existing_results()

    for variant in CONTINUATION_VARIANTS:
        settings = make_settings(variant)
        settings_path = QUALITY_DIR / f"{settings['output_filename']}.json"
        with settings_path.open("w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        append_log(f"Wrote continuation settings for test {variant['index']}: `{settings_path.name}`.")
        append_log(f"Starting continuation test {variant['index']}: `{settings['output_filename']}`.")
        print(f"test_start={variant['index']} name={settings['output_filename']}", flush=True)

        started = time.perf_counter()
        row = {
            "index": variant["index"],
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
            row.update(probe_video(row["generated_files"][0] if row["generated_files"] else ""))
            if row["generated_files"]:
                row["contact_sheet"] = make_contact_sheet(row["generated_files"][0])
        except Exception as exc:
            row["errors"] = [str(exc)]
        row["elapsed_seconds"] = round(time.perf_counter() - started, 1)
        append_log(
            f"Finished continuation test {variant['index']}: success={row['success']}, elapsed={row['elapsed_seconds']}s, "
            f"actual_resolution={row.get('actual_resolution', '')}, fps={row.get('actual_fps', '')}, "
            f"bitrate_mbps={row.get('approx_total_bitrate_mbps', '')}, output=`{row['generated_files'][0] if row['generated_files'] else ''}`."
        )
        if row["errors"]:
            append_log(f"Errors for continuation test {variant['index']}: `{'; '.join(row['errors'])}`.")
        print(f"test_done={variant['index']} elapsed_seconds={row['elapsed_seconds']} success={row['success']}", flush=True)
        results.append(row)
        with RESULTS_JSON.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        write_csv(results)

    append_log("Continuation completed. There are now ten successful outputs if t41-t44 completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
