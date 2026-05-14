from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

from shared.utils import files_locator as fl
from shared.utils.download import download_file, process_files_def


CKPTS = ROOT / "ckpts"
LORA_DIR = ROOT / "loras" / "ltx2"
LOGS = ROOT / "logs"

Q4_URL = "https://huggingface.co/Kijai/LTXV2_comfy/resolve/main/diffusion_models/ltx-2-19b-distilled_Q4_K_M.gguf"
Q4_FILENAME = "ltx-2-19b-distilled_Q4_K_M.gguf"
UNION_CONTROL_LORA_URL = "https://huggingface.co/DeepBeepMeep/LTX-2/resolve/main/ltx-2-19b-ic-lora-union-control-ref0.5.safetensors"

DEEPBEEPMEEP_ROOT_FILES = [
    "ltx-2-spatial-upscaler-x2-1.0.safetensors",
    "ltx-2-temporal-upscaler-x2-1.0.safetensors",
    "ltx-2-19b_vae.safetensors",
    "ltx-2-19b_audio_vae.safetensors",
    "ltx-2-19b_vocoder.safetensors",
    "ltx-2-19b_text_embedding_projection.safetensors",
    "ltx-2-19b-distilled_embeddings_connector.safetensors",
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
GEMMA_TEXT_ENCODER_URL = (
    "https://huggingface.co/DeepBeepMeep/LTX-2/resolve/main/"
    f"{GEMMA_FOLDER}/{GEMMA_FOLDER}_quanto_bf16_int8.safetensors"
)


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
    os.chdir(ROOT)
    LOGS.mkdir(parents=True, exist_ok=True)
    CKPTS.mkdir(parents=True, exist_ok=True)
    LORA_DIR.mkdir(parents=True, exist_ok=True)
    fl.set_checkpoints_paths(["ckpts", "."])

    start = time.time()
    print("[info] LTX-2 Q4_K_M asset download starting", flush=True)
    print(f"[info] WanGP root: {ROOT}", flush=True)

    expected_paths: list[Path] = [CKPTS / Q4_FILENAME]
    expected_paths += [CKPTS / name for name in DEEPBEEPMEEP_ROOT_FILES]
    expected_paths += [CKPTS / GEMMA_FOLDER / name for name in GEMMA_FILES]
    expected_paths.append(CKPTS / GEMMA_FOLDER / f"{GEMMA_FOLDER}_quanto_bf16_int8.safetensors")
    expected_paths.append(LORA_DIR / "ltx-2-19b-ic-lora-union-control-ref0.5.safetensors")

    before_sizes = {str(path): file_size(path) for path in expected_paths}

    ensure_download(Q4_URL, CKPTS / Q4_FILENAME)

    process_files_def(
        repoId="DeepBeepMeep/LTX-2",
        sourceFolderList=[""],
        fileList=[DEEPBEEPMEEP_ROOT_FILES],
    )
    process_files_def(
        repoId="DeepBeepMeep/LTX-2",
        sourceFolderList=[GEMMA_FOLDER],
        fileList=[GEMMA_FILES],
    )
    ensure_download(GEMMA_TEXT_ENCODER_URL, CKPTS / GEMMA_FOLDER / f"{GEMMA_FOLDER}_quanto_bf16_int8.safetensors")
    ensure_download(UNION_CONTROL_LORA_URL, LORA_DIR / "ltx-2-19b-ic-lora-union-control-ref0.5.safetensors")

    after_sizes = {str(path): file_size(path) for path in expected_paths}
    missing = [str(path) for path in expected_paths if after_sizes[str(path)] <= 0]
    if missing:
        raise RuntimeError("Missing expected files:\n" + "\n".join(missing))

    total_size = sum(after_sizes.values())
    newly_downloaded = sum(max(after_sizes[path] - before_sizes.get(path, 0), 0) for path in after_sizes)
    summary = {
        "variant": "LTX-2 2.0 19B Distilled GGUF Q4_K_M",
        "q4_url": Q4_URL,
        "started_at_epoch": start,
        "finished_at_epoch": time.time(),
        "elapsed_seconds": time.time() - start,
        "total_expected_asset_bytes": total_size,
        "newly_downloaded_bytes": newly_downloaded,
        "files": [
            {
                "path": str(path.resolve()),
                "bytes": after_sizes[str(path)],
                "size": bytes_fmt(after_sizes[str(path)]),
            }
            for path in expected_paths
        ],
    }
    summary_path = LOGS / "ltx2_q4_download_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[summary] total expected LTX-2 Q4 assets: {bytes_fmt(total_size)}", flush=True)
    print(f"[summary] newly downloaded this run: {bytes_fmt(newly_downloaded)}", flush=True)
    print(f"[summary] wrote {summary_path}", flush=True)


if __name__ == "__main__":
    main()
