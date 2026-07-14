# Contributing / المساهمة

Help build an **open** corpus of which faults appear on which PS4 model/FW —
the kind of data that is otherwise locked inside private, closed tools.

ساعد في بناء **corpus مفتوح** يربط الأعطال بكل موديل/FW من PS4 — وهي بيانات
مقفلة عادةً داخل أدوات مغلقة.

## How to contribute / خطوات المساهمة
1. Scan/repair your dump with **PS4 NOR EASYTOOL V1**.
   افحص/أصلح دمبتك باستخدام **PS4 NOR EASYTOOL V1**.
2. Click **Export report** (GUI) or run:
   شغّل زر **تصدير التقرير** (الواجهة) أو:
   ```bash
   python -c "import main; main.export_report('path/to/dump.bin','nor','my.report.json')"
   ```
3. The file contains **no serial / MAC / HDD** data — only model, FW,
   health and faulty regions. Review it; if comfortable, submit it.
   الملف **لا يحوي سيريال/MAC/قرص** — فقط الموديل وFW والصحة والمناطق المعطوبة.
   راجعه، وإن ارتحت قدّمه.
4. Open a pull request adding `my.report.json` to `community/corpus/`,
   or email/DM it to the maintainer.
   افتح طلب سحب بإضافة `my.report.json` إلى `community/corpus/`، أو أرسله
   للقائم على المشروع.
5. Maintainers run `python scripts/aggregate.py --json` to refresh public
   statistics (`community/stats.json`).
   يشغّل القائمون `python scripts/aggregate.py --json` لتحديث الإحصاءات العامة.

## Rules / القواعد
- **Anonymize:** never edit a report to add serial/MAC/HDD/board-id. Reports
  are rejected if they contain identity data.
  **جّهل:** لا تضف سيريال/MAC/قرص/board-id أبدًا. تُرفض التقارير ذات الهوية.
- One report per dump is enough; re-submit only if the dump changes.
  تقرير واحد لكل دمبة يكفي.
- Label the file with model + FW when possible (e.g. `cuh22-fw13.02.report.json`).
  سمّ الملف بالموديل وFW إن أمكن.
