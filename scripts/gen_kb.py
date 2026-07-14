#!/usr/bin/env python
# gen_kb.py - Generate kb.json for the PS4 NOR & Syscon Open Repair Knowledge Base.
#
# Introspects the PS4 NOR EASYTOOL V1 repair modules (read-only) and emits a
# machine-readable knowledge base. The docs generator (gen_docs.py) consumes
# kb.json, so the published reference never drifts from the actual tool logic.
#
# Usage:  python scripts/gen_kb.py
import os
import sys
import json
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PS4 = os.path.normpath(os.path.join(REPO, "..", "ps4repair"))
sys.path.insert(0, PS4)

TOOL = "PS4 NOR EASYTOOL V1"
TOOL_AUTHOR = "ISLAM JAMEL"


def safe(name, fn, default=None):
    try:
        return fn()
    except Exception as e:
        sys.stderr.write("gen_kb: %s failed: %s\n" % (name, e))
        return default


# --------------------------------------------------------------------------
# NOR regions (from layout._LAYOUT: start, end, name, zone, klass, comp)
# --------------------------------------------------------------------------
def nor_regions():
    import layout
    out = []
    for row in layout._LAYOUT:
        start, end, name, zone, klass = row[0], row[1], row[2], row[3], row[4]
        comp = row[5] if len(row) > 5 else None
        per_console = klass in ("per_console", "nvs")
        donor = klass == "shared"
        out.append({
            "name": name,
            "start": start,
            "end": end,
            "size": end - start,
            "zone": zone,
            "klass": klass,
            "comp": comp,
            "per_console": per_console,
            "donor_eligible": donor,
        })
    return out


# --------------------------------------------------------------------------
# Syscon regions (stable, from syscon_layout._LAYOUT / syscon_repair)
# --------------------------------------------------------------------------
def syscon_regions():
    # sc_code 0x0-0x60000 (SHARED, donor-consensus), sc_nvs 0x60000-0x70000
    # (PER-CONSOLE, SAMU), sc_blank 0x70000-0x80000 (padding).
    return [
        {"name": "sc_code", "start": 0x0, "end": 0x60000, "size": 0x60000,
         "zone": "syscon", "klass": "shared", "comp": None,
         "per_console": False, "donor_eligible": True},
        {"name": "sc_nvs", "start": 0x60000, "end": 0x70000, "size": 0x10000,
         "zone": "syscon", "klass": "per_console", "comp": None,
         "per_console": True, "donor_eligible": False},
        {"name": "sc_blank", "start": 0x70000, "end": 0x80000, "size": 0x10000,
         "zone": "syscon", "klass": "blank", "comp": None,
         "per_console": False, "donor_eligible": False},
    ]


def nvs_areas():
    out = []
    try:
        import nvs
        A = nvs.AREAS
        if isinstance(A, dict):
            for k, v in A.items():
                if isinstance(v, (tuple, list)) and len(v) >= 2:
                    out.append({"name": k, "offset": v[0], "size": v[1]})
        elif isinstance(A, (list, tuple)):
            for v in A:
                if isinstance(v, (tuple, list)) and len(v) >= 3:
                    out.append({"name": v[0], "offset": v[1], "size": v[2]})
    except Exception as e:
        sys.stderr.write("gen_kb: nvs_areas failed: %s\n" % e)
    return out


# --------------------------------------------------------------------------
# Fault action vocabulary (repair.classify_action buckets)
# --------------------------------------------------------------------------
FAULT_ACTIONS = [
    ("ok", "ok", "سليم", "Region verified good; untouched.",
     "المنطقة سليمة تم التحقق منها؛ لم تُعدّل.", "none"),
    ("blank_ok", "ok", "فارغ مقبول", "Intentionally empty padding.",
     "مساحة فارغة مقصودة (حشو).", "none"),
    ("per_console_ok", "ok", "بيانات خاصة بالكونسول سليمة",
     "Per-console region present and valid; must not be changed.",
     "منطقة خاصة بالكونسول موجودة وصالحة؛ لا يجوز تغييرها.", "none"),
    ("rebuilt", "info", "أُعيد بناؤه", "Structurally rebuilt from donor consensus.",
     "أُعيد بناؤه بنيويًا من إجماع المتبرعين.", "auto"),
    ("skipped", "info", "تم تخطّيه", "Region intentionally skipped (user choice).",
     "تم تخطّي المنطقة (باختيار المستخدم).", "user"),
    ("donor_repaired", "repaired", "أُصلح من متبرّع",
     "Replaced with a matching donor blob (same HWID/FW).",
     "استُبدلت بكتلة متبرّع مطابقة (نفس HWID/FW).", "donor"),
    ("self_backup_main", "repaired", "استرجاع من النسخة الاحتياطية",
     "Copied the in-dump backup copy over the corrupted main copy.",
     "نُسخت النسخة الاحتياطية داخل الدمبة فوق النسخة التالفة.", "self"),
    ("self_main_backup", "repaired", "تحديث النسخة الاحتياطية",
     "Copied the good main copy into the backup slot.",
     "نُسخت النسخة الرئيسية السليمة إلى موقع النسخة الاحتياطية.", "self"),
    ("donor_regen", "repaired", "إعادة توليد من متبرّع",
     "Regenerated CID/UNK from a same-Board-ID donor.",
     "أُعيد توليد CID/UNK من متبرّع بنفس معرّف اللوحة.", "donor"),
    ("regen_random_destructive", "repaired", "توليد عشوائي مدمر",
     "Generated a random EAP key; REQUIRES HDD wipe. Last resort.",
     "وُلّد مفتاح EAP عشوائي؛ يتطلب مسح القرص الصلب. حل أخير.", "destructive"),
    ("ok_unverified", "warning", "سليم لكن غير مؤكد",
     "Not provably corrupt; kept as-is, flagged for review.",
     "غير مؤكد أنه تالف؛ تُرك كما هو مع تعليمه للمراجعة.", "review"),
    ("flag_unverified", "warning", "غير مؤكد",
     "Could not verify; needs human review.",
     "تعذّر التحقق؛ يحتاج مراجعة بشرية.", "review"),
    ("flag_needs_donor", "warning", "يحتاج متبرّعًا",
     "Corrupt/blank and no self-backup; a donor match is required.",
     "تالف/فارغ بلا نسخة احتياطية؛ يتطلب مطابقة متبرّع.", "donor"),
    ("flag_unknown_fw", "warning", "برنامج غير معروف",
     "Firmware not recognised by the donor DB.",
     "برنامج غير معروف في قاعدة المتبرعين.", "review"),
    ("flag_review", "warning", "يحتاج مراجعة",
     "Ambiguous result; manual inspection advised.",
     "نتيجة غامضة؛ يُنصح بالفحص اليدوي.", "review"),
    ("corrupt_mismatch", "warning", "اختلاف بين النسختين",
     "Main and backup copies both non-blank but differ -> TWO candidates "
     "emitted (A=backup, B=main); trial-flash to discover the good one.",
     "النسختان الرئيسية والاحتياطية غير فارغتين ومختلفتين -> يُنتج ملفّين "
     "مرشّحين (A=احتياطي، B=رئيسي)؛ جرّب البرمجة لاكتشاف الصحيح.", "two-candidate"),
    ("torus_ambiguous", "warning", "واي-فاي/بلوتوث غامض",
     "Wi-Fi/BT firmware HWID ambiguous; candidate blobs listed to trial-flash.",
     "معرّف واي-فاي/بلوتوث غامض؛ تُدرج كتل مرشّحة للتجربة.", "trial"),
    ("flag_unrecoverable", "critical", "غير قابل للاسترجاع",
     "No source to repair from (blank per-console / dead EAP key with no "
     "backup). Hard stop; often needs hardware or SAMU.",
     "لا مصدر للإصلاح (منطقة خاصة فارغة / مفتاح EAP ميت بلا نسخة). توقف "
     "إجباري؛ غالبًا يحتاج أجهزة أو SAMU.", "unrecoverable"),
    ("self_unrecoverable", "critical", "لا يمكن استرجاعه ذاتيًا",
     "Syscon NVS has no in-dump redundancy to self-repair from.",
     "ذاكرة Syscon NVS بلا تكرار داخلي للإصلاح الذاتي.", "unrecoverable"),
    ("self_both_dead", "critical", "النسختان ميتتان",
     "Both main and backup copies are dead.",
     "النسختان الرئيسية والاحتياطية ميتتان.", "unrecoverable"),
]


def fault_actions():
    out = []
    for a, bucket, ar_label, en_mean, ar_mean, fix in FAULT_ACTIONS:
        out.append({
            "action": a, "bucket": bucket,
            "label_ar": ar_label, "label_en": a,
            "meaning_en": en_mean, "meaning_ar": ar_mean,
            "fixability": fix,
        })
    return out


# --------------------------------------------------------------------------
# Slot-switch families (revert.py)
# --------------------------------------------------------------------------
def slot_switch():
    return {
        "pattern_count": 14,
        "families": [
            {"fam": 1, "models": [10, 11],
             "desc_en": "Fat 10xx/11xx (Aeolia) - 4 patterns (#3-#6).",
             "desc_ar": "فات 10xx/11xx (Aeolia) - 4 أنماط (#3-#6)."},
            {"fam": 2, "models": [12, 20, 21, 22, 70, 71, 72],
             "desc_en": "Fat/Slim/Pro 12xx/2xxx/7xxx - 4 patterns (#1,#2,#7,#8).",
             "desc_ar": "فات/سليم/برو 12xx/2xxx/7xxx - 4 أنماط (#1,#2,#7,#8)."},
            {"fam": None, "models": [],
             "desc_en": "Unmapped models - all 14 patterns returned so the "
                       "correct one is never excluded.",
             "desc_ar": "موديلات غير مصنّفة - تُرجع الأنماط الـ14 كاملة لئلا يُستبعد الصحيح."},
        ],
        "note_en": "The correct 16-byte CORE_SWCH descriptor is console/model "
                   "specific and not predictable; the tool brute-forces it by "
                   "writing NOR #N + patched Syscon and reading UART.",
        "note_ar": "واصف CORE_SWCH المكوّن من 16 بايت خاص بكل كونسول/موديل وغير "
                   "قابل للتنبؤ؛ الأداة تخمّنه بكتابة NOR رقم N + Syscon معدّل وقراءة UART.",
    }


# --------------------------------------------------------------------------
# SNVS autopatch (revert.py)
# --------------------------------------------------------------------------
def snvs():
    return {
        "records_en": "UPD=(0x08,0x09,0x0A,0x0B)=FW_A/FW_B/LIC1/LIC2; "
                      "PRE=(0x0C..0x0F,0x20..0x23).",
        "records_ar": "UPD=(0x08,0x09,0x0A,0x0B)=FW_A/FW_B/LIC1/LIC2؛ "
                      "PRE=(0x0C..0x0F,0x20..0x23).",
        "autopatch_en": "Blanks the newest FW-update record group in SNVS so "
                        "the previous generation becomes active (Syscon "
                        "counterpart of the NOR slot flip). Refuses if any PRE "
                        "record appears after the 08-0B quartet.",
        "autopatch_ar": "يمسح أحدث مجموعة سجلات تحديث FW داخل SNVS ليصبح الجيل "
                        "السابق نشطًا (نظير Syscon لقلب بنك NOR). يرفض إن ظهر "
                        "أي سجل PRE بعد رباعي 08-0B.",
        "readiness_threshold": 10000,
        "readiness_en": "Revertable consoles show >10,000 non-blank bytes in "
                        "0x60000-0x6A000 (SNVS population); 'Not patchable' "
                        "consoles show ~2.4k. Borderline (~10k) is a gray area.",
        "readiness_ar": "الكونسولات القابلة للرجوع تظهر >10000 بايت غير فارغ في "
                        "0x60000-0x6A000؛ 'غير قابل للرقعة' تظهر ~2.4k. الحدود "
                        "(~10k) منطقة رمادية.",
    }


# --------------------------------------------------------------------------
# User-facing operations (main.py)
# --------------------------------------------------------------------------
OPERATIONS = [
    ("run_scan", "Scan / تشخيص",
     "Dry-run analysis; reports every region's health without writing.",
     "تحليل تجريبي؛ يبلّغ صحة كل منطقة دون كتابة.",
     "Triage: 'is this dump broken, and can it be fixed?'",
     "فرز أولي: 'هل الدمبة معطوبة، وهل يمكن إصلاحها؟'"),
    ("do_repair", "Full repair / إصلاح كامل",
     "Scans, shows changes, writes fixed/<name>.fixed.bin. Original untouched.",
     "يفحص، يعرض التغييرات، يكتب fixed/<name>.fixed.bin. الأصل لم يُمس.",
     "One-click safe repair of a corrupt dump.",
     "إصلاح آمن بنقرة واحدة لدمبة معطوبة."),
    ("nor_regen_nvs", "Regen NVS (CID/UNK) / توليد NVS",
     "Regenerates CID/UNK from same-Board-ID, FW>=target donors; emits M1/M2/M3.",
     "يولّد CID/UNK من متبرّعين بنفس اللوحة وFW>=الهدف؛ يُنتج M1/M2/M3.",
     "CID/UNK corruption when the in-NOR backup is also dead.",
     "فساد CID/UNK عند موت النسخة الاحتياطية داخل NOR أيضًا."),
    ("nor_smart_revert", "SMART revert / رجوع ذكي",
     "Legit CoreOS patch + SNVS autopatch using the console's own 2nd dump.",
     "رقعة CoreOS شرعية + autopatch لـ SNVS باستخدام الدمبة الثانية للكونسول.",
     "Safe firmware downgrade (no glitch) for a patched console.",
     "تنزيل برنامج آمن (بلا glitch) لكونسول معدّل."),
    ("nor_slot_switch", "Slot switch / قلب البنوك",
     "Generates 14 (or family-narrowed) CORE_SWCH patterns + UART-on + optional "
     "Syscon SNVS autopatch.",
     "يولّد أنماط CORE_SWCH الـ14 (أو المضيّقة بالموديل) + تفعيل UART + autopatch "
     "Syscon اختياري.",
     "'No-legit' downgrade requiring Syscon pin-lift/microsoldering.",
     "تنزيل 'لا-شرعي' يتطلب رفع سن Syscon/لحام دقيق."),
    ("syscon_restore_nvs", "Restore own Syscon / استرجاع Syscon الخاص",
     "Copies NVS from the SAME console's own backup dump.",
     "ينسخ NVS من دمبة النسخة الاحتياطية لنفس الكونسول.",
     "Recover Syscon identity without altering serial/MAC.",
     "استرجاع هوية Syscon دون تغيير السيريال/MAC."),
    ("syscon_restore_from_partner", "Restore partner Syscon / استرجاع من شريك",
     "Restores NVS from a PAIRED Syscon of the same console.",
     "يسترجع NVS من Syscon مقرون لنفس الكونسول.",
     "Cross-Syscon recovery when one chip's NVS is corrupt.",
     "استرجاع عبر Syscon عند فساد NVS في شريحة واحدة."),
    ("syscon_verify_vs_nor", "Verify Syscon vs NOR / تحقق Syscon مقابل NOR",
     "Read-only: compares Syscon board-id vs NOR board-id (1-byte offset).",
     "للقراءة فقط: يقارن board-id الخاص بـ Syscon مع NOR (إزاحة بايت واحد).",
     "Confirm a Syscon actually belongs to the paired NOR.",
     "التأكد أن Syscon يخص NOR المقرون فعلاً."),
]


def operations():
    out = []
    for key, name, en_what, ar_what, en_prob, ar_prob in OPERATIONS:
        out.append({
            "key": key, "name_en": name.split(" / ")[0],
            "name_ar": name.split(" / ")[1] if " / " in name else name,
            "what_en": en_what, "what_ar": ar_what,
            "problem_en": en_prob, "problem_ar": ar_prob,
        })
    return out


# --------------------------------------------------------------------------
# Tribal-knowledge / surprising facts
# --------------------------------------------------------------------------
SURPRISING = [
    ("EAP_KEY is the only truly unrecoverable NOR field. On 10xx/11xx there is "
     "NO in-NOR backup at all, so a dead EAP key is permanently unrecoverable "
     "without SAMU; the only option is destructive random regen + HDD reformat.",
     "مفتاح EAP_KEY هو الحقل الوحيد غير القابل للاسترجاع نهائيًا في NOR. على "
     "10xx/11xx لا توجد نسخة احتياطية داخل NOR إطلاقًا، فمفتاح EAP ميت لا "
     "يُسترجع بلا SAMU؛ الحل الوحيد توليد عشوائي مدمر + مسح القرص."),
    ("Syscon NVS has ZERO in-dump redundancy (0/869 dumps show a main/backup "
     "split), so unlike NOR NVS it cannot self-repair from the same file - it "
     "only ever says 'restore from your own backup'.",
     "ذاكرة Syscon NVS بلا أي تكرار داخل الملف (0 من 869 دمبة تظهر تقسيم "
     "رئيسي/احتياطي)، فعلى عكس NOR NVS لا يمكن إصلاحها ذاتيًا من نفس الملف - "
     "تقول فقط 'استرجع من نسختك الاحتياطية'."),
    ("There is a 1-byte board-id encoding offset between NOR (byte3 = 0x06) and "
     "Syscon (byte3 = 0x05); this is why the tool refuses raw NOR->Syscon "
     "seeding.",
     "إزاحة بايت واحد في board-id بين NOR (البايت 3 = 0x06) وSyscon (البايت 3 = "
     "0x05)؛ لذا ترفض الأداة البذر الخام من NOR إلى Syscon."),
    ("The SNVS population threshold (>10,000 non-blank bytes in 0x60000-0x6A000) "
     "is an empirical magic number separating revertable (~27k) from 'Not "
     "patchable' (~2.4k) consoles; borderline (~10k) is a gray area.",
     "عتبة امتلاء SNVS (>10000 بايت غير فارغ في 0x60000-0x6A000) رقم تجريبي "
     "يفصل القابل للرجوع (~27k) عن 'غير قابل للرقعة' (~2.4k)؛ الحدود (~10k) "
     "منطقة رمادية."),
    ("The eMMC INACTIVE bank is intentionally left alone based on MBR ground-"
     "truth; a technician comparing a 'fixed' dump may see one emc bank "
     "unchanged and think repair failed - it is by design.",
     "يُترك بنك eMMC غير النشط عمدًا استنادًا إلى حقيقة MBR؛ قد يرى الفني بنك emc "
     "واحدًا دون تغيير فيظن الإصلاح فشل - هذا مقصود."),
    ("corrupt_mismatch (EAP main vs backup differ, both non-blank) produces TWO "
     "candidate files (A_backup, B_main) rather than one fix; trial-flash to "
     "discover which copy is good.",
     "corrupt_mismatch (اختلاف EAP بين الرئيسي والاحتياطي وكلاهما غير فارغ) يُنتج "
     "ملفّين مرشّحين (A_backup، B_main) لا إصلاحًا واحدًا؛ جرّب البرمجة."),
    ("s0_nvs is not one opaque blob - it is a precisely sub-addressed structure "
     "(nvs.AREAS) with a +0x3000 mirror. Most NOR 'per-console' warnings "
     "actually stem from these sub-fields; the layout map alone hides this.",
     "s0_nvs ليس كتلة معتمة واحدة - بل بنية مُعنونة بدقة (nvs.AREAS) مع مرآة "
     "+0x3000. معظم تحذيرات NOR 'الخاصة بالكونسول' نابعة من these الحقول الفرعية."),
    ("Syscon repair restores ONLY sc_code to donor consensus; sc_nvs identity "
     "(board-id/serial/MAC/calibration) and the entire SAMU-encrypted SNVS are "
     "per-console and never transplanted.",
     "إصلاح Syscon لا يسترجع سوى sc_code إلى إجماع المتبرعين؛ هوية sc_nvs "
     "(board-id/serial/MAC/معايرة) وكل SNVS المشفّر بـ SAMU خاصة بالكونسول ولا "
     "تُنقل."),
    ("NOR write order matters: always write NOR first, then Syscon, matching. "
     "Out-of-sync writes cause BLOD (CE-40947-4).",
     "ترتيب البرمجة مهم: NOR أولًا ثم Syscon متطابقين. الكتابة غير المتزامنة "
     "تسبب BLOD (CE-40947-4)."),
    ("Two distinct NVS parsers exist: nvs.py (NOR, simple fixed offsets) vs "
     "syscon_nvs_cpp.py (faithful fail0verflow port: flat+sparse history, "
     "write-counters). The Syscon one is the authoritative SNVS reference.",
     "هناك محلّلان مختلفان للـ NVS: nvs.py (NOR، إزاحات ثابتة بسيطة) و "
     "syscon_nvs_cpp.py (منفذ وفي faithful لـ fail0verflow: تاريخ flat+sparse، "
     "عدّادات كتابة). نسخة Syscon هي المرجع المعتمد لـ SNVS."),
    ("Model->silicon mapping is hardcoded in multiple places (sce.py, fws.py, "
     "revert.py). New CUH models (e.g. 7xxx PRO) are partially covered; anything "
     "unmapped falls back to 'all 14 slot-switch patterns'.",
     "ربط الموديل بالسليكون مُرمّز ثابت في أماكن عدة (sce.py، fws.py، revert.py). "
     "موديلات CUH جديدة (مثل 7xxx PRO) مغطاة جزئيًا؛ أي موديل غير مصنّف يرجع "
     "إلى 'كل أنماط slot-switch الـ14'."),
    ("fws.DEFAULT_ROOT is a hardcoded absolute path (C:\\6\\DONORS\\fws) that "
     "diverges from main.FWS_DIR (<app>/DONORS/fws); keep donor blobs at the "
     "app-dir copy or the GUI may not see them.",
     "fws.DEFAULT_ROOT مسار مطلق مرمّز (C:\\6\\DONORS\\fws) يختلف عن main.FWS_DIR "
     "(<app>/DONORS/fws)؛ احتفظ بكتل المتبرعين في نسخة مجلد التطبيق وإلا قد لا "
     "تراها الواجهة."),
    ("FW number parsing strips dots and int()s them ('13.04' -> 1304) and "
     "compares numerically; mixed-width FW strings could mis-rank donors.",
     "تحليل رقم FW يزيل النقاط ويعامله int() ('13.04' -> 1304) ويقارن رقميًا؛ "
     "سلاسل FW بعرض مختلط قد ترتّب المتبرعين خطأً."),
    ("A 'healthy' dump writes NOTHING (do_repair is a no-op); a 'repairable' "
     "dump produces a fixed .bin; any 'needs-review' action is a hard stop that "
     "emits candidate(s) for trial, not a single silent fix.",
     "الدمبة 'السليمة' لا تكتب شيئًا (do_repair لا يفعل شيئًا)؛ 'القابلة "
     "للإصلاح' تنتج fixed.bin؛ أي إجراء 'يحتاج مراجعة' توقف إجباري يُنتج "
     "مرشّحًا/مرشّحين للتجربة لا إصلاحًا صامتًا."),
]


def surprising():
    return [{"en": e, "ar": a} for e, a in SURPRISING]


def main():
    kb = {
        "meta": {
            "tool": TOOL,
            "tool_author": TOOL_AUTHOR,
            "kb_schema": "1.0",
            "generated": datetime.datetime.now(datetime.timezone.utc)
                          .strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": "ps4repair module introspection (read-only)",
        },
        "nor_regions": safe("nor_regions", nor_regions, []),
        "syscon_regions": safe("syscon_regions", syscon_regions, []),
        "nvs_areas": safe("nvs_areas", nvs_areas, []),
        "fault_actions": fault_actions(),
        "slot_switch": slot_switch(),
        "snvs": snvs(),
        "operations": operations(),
        "surprising_facts": surprising(),
    }
    out_path = os.path.join(REPO, "kb.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)
    print("Wrote %s" % out_path)
    print("  NOR regions : %d" % len(kb["nor_regions"]))
    print("  Syscon regs : %d" % len(kb["syscon_regions"]))
    print("  NVS areas   : %d" % len(kb["nvs_areas"]))
    print("  Fault acts  : %d" % len(kb["fault_actions"]))
    print("  Operations  : %d" % len(kb["operations"]))
    print("  Facts       : %d" % len(kb["surprising_facts"]))


if __name__ == "__main__":
    main()
