# Downgrade & slot-switch

## Model family

| Model family | CUH | Patterns | Meaning |
|---|---|---|---|
| 1 | CUH-10xx, CUH-11xx | 14 | Fat 10xx/11xx (Aeolia) - 4 patterns (#3-#6). |
| 2 | CUH-12xx, CUH-20xx, CUH-21xx, CUH-22xx, CUH-70xx, CUH-71xx, CUH-72xx | 14 | Fat/Slim/Pro 12xx/2xxx/7xxx - 4 patterns (#1,#2,#7,#8). |
| all | all unmapped | 14 | Unmapped models - all 14 patterns returned so the correct one is never excluded. |

> The correct 16-byte CORE_SWCH descriptor is console/model specific and not predictable; the tool brute-forces it by writing NOR #N + patched Syscon and reading UART.

## SNVS autopatch

- UPD=(0x08,0x09,0x0A,0x0B)=FW_A/FW_B/LIC1/LIC2; PRE=(0x0C..0x0F,0x20..0x23).
- Blanks the newest FW-update record group in SNVS so the previous generation becomes active (Syscon counterpart of the NOR slot flip). Refuses if any PRE record appears after the 08-0B quartet.
- Revertable consoles show >10,000 non-blank bytes in 0x60000-0x6A000 (SNVS population); 'Not patchable' consoles show ~2.4k. Borderline (~10k) is a gray area. (threshold=10000)

[Back to index](index.md)
