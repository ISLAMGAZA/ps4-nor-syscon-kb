# Release v1.0 (draft)

## Binaries (attach to the GitHub Release)
- `PS4_NOR_EASYTOOL_V1_GUI.exe` — graphical interface (Windows).
- `PS4_NOR_EASYTOOL_V1.exe` — console tool.

## Highlights
- **NOR & Syscon**: scan / repair / NVS regen / SMART revert / slot switch.
- In-app **About**, **How-to**, and **Submit to corpus** (anonymized upload).
- **Open Repair Knowledge Base** (`kb.json`) + bilingual docs (`docs/en`,
  `docs/ar`, `docs/index.html` with AR/EN toggle).
- Community **corpus** with auto-aggregated `community/stats.json` (GitHub
  Action on every corpus change).

## Build from source
```
cd ps4repair
powershell -ExecutionPolicy Bypass -File build_gui.ps1
```
Requires Python + PyInstaller; the watermelon icon and `about.json` are
bundled automatically.

## Before repairing
Rebuild the donor indexes once from the app: **NOR ▸ Advanced** and
**Syscon ▸ Advanced**.

## Security
- Revoke and **never share** GitHub tokens. The app uses your local `gh` CLI
  authentication — the token never enters the code or this repository.
