# NOR flash regions (32 MB sflash0)

| Region | Offset | Size | Class | Per-console | Donor | What it holds |
|---|---|---|---|---|---|---|
| s0_header | 0x0 | 0x1000 | struct | no | no | Deterministic s0 header / partition table - rebuildable from donor consensus. |
| s0_active_slot | 0x1000 | 0x1000 | struct | no | no | Deterministic s0 header / partition table - rebuildable from donor consensus. |
| s0_mbr1 | 0x2000 | 0x1000 | struct | no | no | Deterministic s0 header / partition table - rebuildable from donor consensus. |
| s0_mbr2 | 0x3000 | 0x1000 | struct | no | no | Deterministic s0 header / partition table - rebuildable from donor consensus. |
| s0_emc_ipl_a | 0x4000 | 0x60000 | shared | no | yes | eMMC IPL bootloader - donor-matched by HWID + FW. |
| s0_emc_ipl_b | 0x64000 | 0x60000 | shared | no | yes | eMMC IPL bootloader - donor-matched by HWID + FW. |
| s0_eap_kbl | 0xC4000 | 0x80000 | shared | no | yes | EAP keyboot loader - donor-matched by HWID + FW. |
| s0_wifi | 0x144000 | 0x80000 | shared | no | yes | Wi-Fi / BT (Torus) firmware - donor-matched by HWID + FW. |
| s0_nvs | 0x1C4000 | 0xC000 | per_console | yes | no | NOR NVS (CID/UNK/EAP) - per-console; an in-NOR backup exists on 12xx+ models. |
| s0_blank | 0x1D0000 | 0x30000 | blank | no | no | Unused padding. |
| s1_header | 0x200000 | 0x1000 | per_console | yes | no | Per-console encrypted region - never transplant. |
| s1_active_slot | 0x201000 | 0x1000 | per_console | yes | no | Per-console encrypted region - never transplant. |
| s1_mbr1 | 0x202000 | 0x1000 | per_console | yes | no | Per-console encrypted region - never transplant. |
| s1_mbr2 | 0x203000 | 0x1000 | per_console | yes | no | Per-console encrypted region - never transplant. |
| s1_sam_ipl_a | 0x204000 | 0x3E000 | per_console | yes | no | Per-console encrypted region - never transplant. |
| s1_sam_ipl_b | 0x242000 | 0x3E000 | per_console | yes | no | Per-console encrypted region - never transplant. |
| s1_idata | 0x280000 | 0x80000 | per_console | yes | no | Per-console encrypted region - never transplant. |
| s1_bd_hrl | 0x300000 | 0x80000 | per_console | yes | no | Per-console encrypted region - never transplant. |
| s1_vtrm | 0x380000 | 0x40000 | per_console | yes | no | Per-console encrypted region - never transplant. |
| s1_coreos_b | 0x3C0000 | 0xCC0000 | per_console | yes | no | Per-console encrypted region - never transplant. |
| s1_coreos_a | 0x1080000 | 0xCC0000 | per_console | yes | no | Per-console encrypted region - never transplant. |
| s1_blank | 0x1D40000 | 0x2C0000 | blank | no | no | Unused padding. |

[Back to index](index.md)
