# Wan2GP UGC Pipeline Version Control

This repo is the source of truth for lightweight Wan2GP/LTX-2.3 pipeline state.

Track:

- `settings/*.json` for model-family UI/runtime settings.
- `wgp_config.json` and `envs.json` for the current local architecture and selected runtime profile.
- `_quality_tests/*.json`, `_quality_tests/*.md`, `_quality_tests/*.csv`, and `_quality_tests/*.py` for experiment settings, trackers, notes, and reproducible test runners.
- Small prompt files, registry files, and Codex skill notes under `ugcvideos/`.

Do not track:

- Generated videos such as `.mp4`, `.mov`, `.mkv`, or `.webm`.
- Generated contact sheets or image outputs unless they are intentionally promoted as small reference assets.
- Model weights, LoRAs, checkpoints, archives, runtime logs, caches, and local process files.

For future video improvements, commit the settings and experiment metadata first. Keep the heavy outputs in local storage or a separate artifact store, and reference them from markdown notes when needed.
