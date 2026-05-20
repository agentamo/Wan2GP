from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.api import init


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", required=True)
    parser.add_argument("--copy-to", default="")
    args = parser.parse_args()

    root = ROOT
    settings_path = Path(args.settings)
    if not settings_path.is_absolute():
        settings_path = root / settings_path

    with settings_path.open("r", encoding="utf-8") as f:
        settings = json.load(f)

    output_dir = root / "_quality_tests"
    session = init(root=root, output_dir=output_dir, console_output=False, console_isatty=False)

    start = time.perf_counter()
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
    elapsed = time.perf_counter() - start
    print(f"elapsed_seconds={elapsed:.1f}")
    print(f"success={result.success}")

    for error in result.errors:
        print(f"error={error.message}")

    for generated in result.generated_files:
        print(f"generated={generated}")

    if result.success and args.copy_to and result.generated_files:
        destination = Path(args.copy_to)
        if not destination.is_absolute():
            destination = output_dir / destination
        source = Path(result.generated_files[0]).resolve()
        if source != destination.resolve():
            shutil.copy2(source, destination)
            print(f"copied={destination}")

    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
