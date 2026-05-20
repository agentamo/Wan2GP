from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import hf_hub_download


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", required=True)
    parser.add_argument("--local-dir", required=True)
    args = parser.parse_args()

    path = hf_hub_download(
        repo_id="QuantStack/LTX-2.3-GGUF",
        filename=args.filename,
        local_dir=Path(args.local_dir),
    )
    print(f"downloaded={path}")


if __name__ == "__main__":
    main()
