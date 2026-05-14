@echo off
cd /d "%~dp0.."
set "HF_HUB_OFFLINE=1"
set "TRANSFORMERS_OFFLINE=1"
set "HF_DATASETS_OFFLINE=1"
set "HF_HUB_DISABLE_TELEMETRY=1"
echo [*] Offline mode enabled. WanGP will use local model files only.
call "scripts\run.bat"
