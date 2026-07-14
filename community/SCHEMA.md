# Report JSON Schema / مخطط تقرير JSON

Every report is produced by `main.export_report()` in **PS4 NOR EASYTOOL V1**
(or the GUI **Export report** button). It is intentionally **anonymized**:
no serial, MAC, HDD or board-id is included.

كل تقرير يُنتج بواسطة `main.export_report()` في **PS4 NOR EASYTOOL V1** (أو زر
**تصدير التقرير** في الواجهة). وهو **لا يكشف هوية الجهاز عمدًا**: لا سيريال ولا MAC ولا بيانات
قرص ولا board-id.

## Fields / الحقول

| Field | Type | Description / الوصف |
|-------|------|----------------------|
| `schema` | string | Schema version, currently `"1.0"`. إصدار المخطط. |
| `tool` | string | Always `"PS4 NOR EASYTOOL V1"`. |
| `sub` | string | `"nor"` or `"syscon"`. نوع الدمبة. |
| `model` | int\|null | Console model number (e.g. `22`). رقم الموديل. |
| `sku` | string\|null | SKU string (e.g. `"CUH-2216B B01"`). |
| `fw` | string\|null | Firmware version (e.g. `"13.02"`). |
| `assess` | object | `{status, counts, changes}` health summary. ملخّص الصحة. |
| `assess.status` | string | `healthy` \| `repairable` \| `critical` \| `error`. |
| `assess.counts` | object | Per-action-status counts. عدّادات الحالات. |
| `assess.changes` | int | Number of regions that would change. عدد المناطق المتغيّرة. |
| `faults` | array | Faults needing attention (see below). الأعطال. |
| `regions` | array | Every region: `{region, category, status}`. كل المناطق. |
| `donor_available` | bool | A donor match was found for repair. وُجد متبرّع مطابق. |
| `fingerprint_sha256` | string\|null | Hash of the dump fingerprint (not the dump). بصمة التعرّف. |
| `generated` | string | ISO-8601 UTC timestamp. وقت التوليد. |

### `faults[]` item / عنصر
`{ "region": str, "category": str, "action": str, "note": str, "repairable": bool }`

## Example / مثال
```json
{
  "schema": "1.0",
  "tool": "PS4 NOR EASYTOOL V1",
  "sub": "nor",
  "model": 22,
  "sku": "CUH-2216B B01",
  "fw": "13.02",
  "assess": {"status": "healthy", "counts": {"ok": 20}, "changes": 0},
  "faults": [],
  "regions": [{"region": "s0_header", "category": "STRUCT", "status": "ok"}],
  "donor_available": true,
  "fingerprint_sha256": "a3f...",
  "generated": "2026-07-14T12:00:00Z"
}
```
