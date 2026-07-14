# Syscon regions (512 KB RL78)

| Region | Offset | Size | Class | Per-console | Donor | What it holds |
|---|---|---|---|---|---|---|
| sc_code | 0x0 | 0x60000 | shared | no | yes | None - donor-matched by HWID + FW. |
| sc_nvs | 0x60000 | 0x10000 | per_console | yes | no | Per-console encrypted region - never transplant. |
| sc_blank | 0x70000 | 0x10000 | blank | no | no | Unused padding. |

## NVS vs SNVS

- **sc_nvs** (identity): board-id, serial, MAC, calibration - per-console, never transplant.
- **SNVS**: SAMU-encrypted; downgrade/replay needs hardware glitch + the console's own captured traffic.

[Back to index](index.md)
