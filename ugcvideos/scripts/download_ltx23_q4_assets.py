from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ARCHIVE_ROOT = Path(__file__).resolve().parents[1]
WAN2GP_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WAN2GP_ROOT))
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

from shared.utils import files_locator as fl
from shared.utils.download import download_file, process_files_def


CKPTS = WAN2GP_ROOT / "ckpts"
LORA_DIR = WAN2GP_ROOT / "loras" / "ltx2"
LOGS = ARCHIVE_ROOT / "logs"

Q4_URL = "https://huggingface.co/DeepBeepMeep/LTX-2/resolve/main/ltx-2.3-22b-distilled-Q4_K_M_light.gguf"
Q4_FILENAME = "ltx-2.3-22b-distilled-Q4_K_M_light.gguf"

Q6_URL = "https://huggingface.co/DeepBeepMeep/LTX-2/resolve/main/ltx-2.3-22b-distilled-Q6_K_light.gguf"
Q6_FILENAME = "ltx-2.3-22b-distilled-Q6_K_light.gguf"

LTX23_SUPPORT_FILES = [
    "ltx-2.3-spatial-upscaler-x2-1.1.safetensors",
    "ltx-2.3-temporal-upscaler-x2-1.0.safetensors",
    "ltx-2.3-22b_vae.safetensors",
    "ltx-2.3-22b_audio_vae.safetensors",
    "ltx-2.3-22b_vocoder.safetensors",
    "ltx-2.3-22b_text_embedding_projection.safetensors",
    "ltx-2.3-22b_embeddings_connector.safetensors",
]

GEMMA_FOLDER = "gemma-3-12b-it-qat-q4_0-unquantized"
GEMMA_FILES = [
    "added_tokens.json",
    "chat_template.json",
    "config_light.json",
    "generation_config.json",
    "preprocessor_config.json",
    "processor_config.json",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer.model",
    "tokenizer_config.json",
]
GEMMA_QUANTO_FILENAME = f"{GEMMA_FOLDER}_quanto_bf16_int8.safetensors"
GEMMA_QUANTO_URL = (
    "https://huggingface.co/DeepBeepMeep/LTX-2/resolve/main/"
    f"{GEMMA_FOLDER}/{GEMMA_QUANTO_FILENAME}"
)

UTILITY_LORAS = {
    "union_control_22b": {
        "url": "https://huggingface.co/DeepBeepMeep/LTX-2/resolve/main/ltx-2.3-22b-ic-lora-union-control-ref0.5.safetensors",
        "filename": "ltx-2.3-22b-ic-lora-union-control-ref0.5.safetensors",
        "reason": "Wan2GP built-in LTX-2.3 distilled control LoRA for pose/depth/canny modes.",
    },
    "detailer": {
        "url": "https://huggingface.co/DeepBeepMeep/LTX-2/resolve/main/ltx-2-19b-ic-lora-detailer.safetensors",
        "filename": "ltx-2-19b-ic-lora-detailer.safetensors",
        "reason": "Wan2GP Process Full Video includes this for LTX-2.3 Distilled 1.0 detail passes.",
    },
    "motion_track_control": {
        "url": "https://huggingface.co/Lightricks/LTX-2.3-22b-IC-LoRA-Motion-Track-Control/resolve/main/ltx-2.3-22b-ic-lora-motion-track-control-ref0.5.safetensors",
        "filename": "ltx-2.3-22b-ic-lora-motion-track-control-ref0.5.safetensors",
        "reason": "Official Lightricks LTX-2.3 22B IC-LoRA for sparse trajectory motion control.",
    },
}


def bytes_fmt(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{size} B"


def file_size(path: Path) -> int:
    return path.stat().st_size if path.is_file() else 0


def ensure_download(url: str, target: Path) -> bool:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file() and target.stat().st_size > 0:
        print(f"[skip] {target} ({bytes_fmt(target.stat().st_size)})", flush=True)
        return False
    print(f"[download] {url}", flush=True)
    download_file(url, str(target))
    if not target.is_file() or target.stat().st_size == 0:
        raise RuntimeError(f"Download did not produce a non-empty file: {target}")
    print(f"[ok] {target} ({bytes_fmt(target.stat().st_size)})", flush=True)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Download lean LTX-2.3 22B Q4 assets for Wan2GP.")
    parser.add_argument(
        "--include-q6",
        action="store_true",
        help="Also download Q6_K Light. Leave disabled until Q4 has rendered successfully.",
    )
    parser.add_argument(
        "--skip-utility-loras",
        action="store_true",
        help="Download only the base Q4 model and required support files.",
    )
    args = parser.parse_args()

    os.chdir(WAN2GP_ROOT)
    LOGS.mkdir(parents=True, exist_ok=True)
    CKPTS.mkdir(parents=True, exist_ok=True)
    LORA_DIR.mkdir(parents=True, exist_ok=True)
    fl.set_checkpoints_paths(["ckpts", "."])

    expected_paths: list[Path] = [CKPTS / Q4_FILENAME]
    if args.include_q6:
        expected_paths.append(CKPTS / Q6_FILENAME)
    expected_paths += [CKPTS / name for name in LTX23_SUPPORT_FILES]
    expected_paths += [CKPTS / GEMMA_FOLDER / name for name in GEMMA_FILES]
    expected_paths.append(CKPTS / GEMMA_FOLDER / GEMMA_QUANTO_FILENAME)
    if not args.skip_utility_loras:
        expected_paths += [LORA_DIR / spec["filename"] for spec in UTILITY_LORAS.values()]

    before_sizes = {str(path): file_size(path) for path in expected_paths}
    start = time.time()

    print("[info] LTX-2.3 22B Q4_K_M Light asset download starting", flush=True)
    print(f"[info] Wan2GP root: {WAN2GP_ROOT}", flush=True)
    print(f"[info] UGC archive root: {ARCHIVE_ROOT}", flush=True)
    print("[info] Q6_K Light is not downloaded unless --include-q6 is passed.", flush=True)

    ensure_download(Q4_URL, CKPTS / Q4_FILENAME)
    if args.include_q6:
        ensure_download(Q6_URL, CKPTS / Q6_FILENAME)

    process_files_def(
        repoId="DeepBeepMeep/LTX-2",
        sourceFolderList=[""],
        fileList=[LTX23_SUPPORT_FILES],
    )
    process_files_def(
        repoId="DeepBeepMeep/LTX-2",
        sourceFolderList=[GEMMA_FOLDER],
        fileList=[GEMMA_FILES],
    )
    ensure_download(GEMMA_QUANTO_URL, CKPTS / GEMMA_FOLDER / GEMMA_QUANTO_FILENAME)

    downloaded_loras = {}
    if not args.skip_utility_loras:
        for key, spec in UTILITY_LORAS.items():
            target = LORA_DIR / spec["filename"]
            ensure_download(spec["url"], target)
            downloaded_loras[key] = {
                "path": str(target.resolve()),
                "url": spec["url"],
                "reason": spec["reason"],
            }

    after_sizes = {str(path): file_size(path) for path in expected_paths}
    missing = [str(path) for path in expected_paths if after_sizes[str(path)] <= 0]
    if missing:
        raise RuntimeError("Missing expected files:\n" + "\n".join(missing))

    summary = {
        "variant": "LTX-2.3 22B Distilled 1.0 GGUF Q4_K_M Light",
        "q4_url": Q4_URL,
        "q6_downloaded": bool(args.include_q6),
        "q6_url": Q6_URL if args.include_q6 else None,
        "started_at_epoch": start,
        "finished_at_epoch": time.time(),
        "elapsed_seconds": time.time() - start,
        "total_expected_asset_bytes": sum(after_sizes.values()),
        "newly_downloaded_bytes": sum(
            max(after_sizes[path] - before_sizes.get(path, 0), 0) for path in after_sizes
        ),
        "utility_loras": downloaded_loras,
        "files": [
            {
                "path": str(path.resolve()),
                "bytes": after_sizes[str(path)],
                "size": bytes_fmt(after_sizes[str(path)]),
            }
            for path in expected_paths
        ],
    }
    summary_path = LOGS / "ltx23_q4_download_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[summary] total expected assets: {bytes_fmt(summary['total_expected_asset_bytes'])}", flush=True)
    print(f"[summary] newly downloaded this run: {bytes_fmt(summary['newly_downloaded_bytes'])}", flush=True)
    print(f"[summary] wrote {summary_path}", flush=True)


if __name__ == "__main__":
    main()
