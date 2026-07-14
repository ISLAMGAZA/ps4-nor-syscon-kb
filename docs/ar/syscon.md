# مناطق Syscon (512 كيلو RL78)

| المنطقة | الإزاحة | الحجم | الفئة | خاصة بالكونسول | متبرّع | ما تحتويه |
|---|---|---|---|---|---|---|
| sc_code | 0x0 | 0x60000 | shared | no | yes | None - مطابق من متبرّع حسب HWID + FW. |
| sc_nvs | 0x60000 | 0x10000 | per_console | yes | no | منطقة مشفّرة خاصة بالكونسول - لا تُنقل أبدًا. |
| sc_blank | 0x70000 | 0x10000 | blank | no | no | حشو غير مستخدم. |

## NVS vs SNVS

- **sc_nvs** (identity): board-id, serial, MAC, calibration - per-console, never transplant.
- **sc_nvs** (الهوية): board-id والسيريال وMAC والمعايرة - خاصة بالكونسول، لا تُنقل.
- **SNVS**: SAMU-encrypted; downgrade/replay needs hardware glitch + the console's own captured traffic.
- **SNVS**: مشفّر بـ SAMU؛ الرجوع/التشغيل يحتاج glitch عتادي + مرور الكونسول الملتقط الخاص به.

[العودة إلى الفهرس](index.md)
