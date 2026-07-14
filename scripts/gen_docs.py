#!/usr/bin/env python
# gen_docs.py - Render the bilingual knowledge base from kb.json.
#
# Produces docs/en/*.md, docs/ar/*.md and a single self-contained docs/index.html
# (AR/EN toggle) for the PS4 NOR & Syscon Open Repair Knowledge Base.
#
# Usage:  python scripts/gen_docs.py
import os
import json
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
KB = json.load(open(os.path.join(REPO, "kb.json"), encoding="utf-8"))

DOC = os.path.join(REPO, "docs")

# --------------------------------------------------------------------------
# Bilingual labels
# --------------------------------------------------------------------------
L = {
    "en": {
        "proj": "PS4 NOR & Syscon Open Repair Knowledge Base",
        "sub": "Generated from PS4 NOR EASYTOOL V1 (by ISLAM JAMEL). "
               "Machine-readable source: kb.json.",
        "toc": "Contents",
        "nor": "NOR flash regions (32 MB sflash0)",
        "sys": "Syscon regions (512 KB RL78)",
        "faults": "Fault action vocabulary",
        "down": "Downgrade & slot-switch",
        "manual": "Field manual - tribal knowledge",
        "corpus": "Community corpus (anonymized reports)",
        "name": "Region", "offset": "Offset", "size": "Size", "class": "Class",
        "perc": "Per-console", "donor": "Donor", "meaning": "What it holds",
        "action": "Action", "bucket": "Bucket", "fix": "Fixability",
        "desc": "Meaning", "fam": "Model family", "pat": "Patterns",
        "op": "Operation", "what": "What it does", "prob": "Problem solved",
        "back": "Back to index",
        "gen": "Generated", "lic": "Docs CC-BY-4.0; code MIT. Tool & data "
               "by ISLAM JAMEL.",
    },
    "ar": {
        "proj": "قاعدة معرفة إصلاح PS4 المفتوحة (NOR و Syscon)",
        "sub": "مولّدة من PS4 NOR EASYTOOL V1 (بواسطة ISLAM JAMEL). "
               "المصدر الآلي: kb.json.",
        "toc": "المحتويات",
        "nor": "مناطق NOR (32 ميجا sflash0)",
        "sys": "مناطق Syscon (512 كيلو RL78)",
        "faults": "مفردات إجراءات الأعطال",
        "down": "التنزيل وقلب البنوك",
        "manual": "الدليل الميداني - معرفة تراكمية",
        "corpus": "قاعدة المجتمع (تقارير مُجهّلة)",
        "name": "المنطقة", "offset": "الإزاحة", "size": "الحجم", "class": "الفئة",
        "perc": "خاصة بالكونسول", "donor": "متبرّع", "meaning": "ما تحتويه",
        "action": "الإجراء", "bucket": "الحالة", "fix": "القابلية للإصلاح",
        "desc": "المعنى", "fam": "عائلة الموديل", "pat": "الأنماط",
        "op": "العملية", "what": "ماذا تفعل", "prob": "المشكلة المُحلّة",
        "back": "العودة إلى الفهرس",
        "gen": "وُلّدت في", "lic": "التوثيق CC-BY-4.0؛ الكود MIT. الأداة "
               "والبيانات من ISLAM JAMEL.",
    },
}


def hexf(n):
    return "0x%X" % n


def region_meaning(r, lang):
    klass = r["klass"]
    comp = r.get("comp")
    if klass == "struct":
        return ({
            "en": "Deterministic s0 header / partition table - rebuildable "
                  "from donor consensus.",
            "ar": "رأس / جدول أقسام s0 حتمي - قابل لإعادة البناء من إجماع "
                  "المتبرعين."})[lang]
    if klass == "shared":
        names = {"emc": {"en": "eMMC IPL bootloader",
                        "ar": "مُحمّل إقلاع eMMC IPL"},
                 "eap": {"en": "EAP keyboot loader",
                        "ar": "مُحمّل مفتاح EAP"},
                 "torus": {"en": "Wi-Fi / BT (Torus) firmware",
                          "ar": "برنامج واي-فاي/بلوتوث (Torus)"}}
        nm = names.get(comp, {"en": comp, "ar": comp})[lang]
        return ({
            "en": "%s - donor-matched by HWID + FW." % nm,
            "ar": "%s - مطابق من متبرّع حسب HWID + FW." % nm})[lang]
    if klass == "per_console":
        if r["name"] == "s0_nvs":
            return ({
                "en": "NOR NVS (CID/UNK/EAP) - per-console; an in-NOR backup "
                      "exists on 12xx+ models.",
                "ar": "NOR NVS (CID/UNK/EAP) - خاص بالكونسول؛ نسخة احتياطية "
                      "داخل NOR موجودة على موديلات 12xx+."})[lang]
        return ({
            "en": "Per-console encrypted region - never transplant.",
            "ar": "منطقة مشفّرة خاصة بالكونسول - لا تُنقل أبدًا."})[lang]
    if klass == "blank":
        return ({"en": "Unused padding.", "ar": "حشو غير مستخدم."})[lang]
    return ({"en": "", "ar": ""})[lang]


def build(lang):
    T = L[lang]
    meta = KB["meta"]
    lines = []
    A = lines.append

    def h(n, t):
        A("#" * n + " " + t)

    def tbl(headers, rows):
        A("| " + " | ".join(headers) + " |")
        A("|" + "|".join(["---"] * len(headers)) + "|")
        for r in rows:
            A("| " + " | ".join(str(c) for c in r) + " |")

    # ---- index ----
    h(1, T["proj"])
    A("")
    A("> " + T["sub"])
    A("")
    A("**%s**  " % T["gen"] + meta["generated"] + "  ")
    A("")
    h(2, T["toc"])
    A("- [%s](%s)" % (T["nor"], "nor-regions.html" if lang == "html"
                       else "nor-regions.md"))
    A("- [%s](%s)" % (T["sys"], "syscon.html" if lang == "html"
                       else "syscon.md"))
    A("- [%s](%s)" % (T["faults"], "faults.html" if lang == "html"
                       else "faults.md"))
    A("- [%s](%s)" % (T["down"], "downgrade.html" if lang == "html"
                       else "downgrade.md"))
    A("- [%s](%s)" % (T["manual"], "field-manual.html" if lang == "html"
                       else "field-manual.md"))
    A("- [%s](%s)" % (T["corpus"], "community-corpus.html" if lang == "html"
                       else "community-corpus.md"))
    A("")
    A("*" + T["lic"] + "*")

    return "\n".join(lines)


def build_nor(lang):
    T = L[lang]
    A = []
    ap = A.append

    def h(n, t):
        ap("#" * n + " " + t)

    def tbl(headers, rows):
        ap("| " + " | ".join(headers) + " |")
        ap("|" + "|".join(["---"] * len(headers)) + "|")
        for r in rows:
            ap("| " + " | ".join(str(c) for c in r) + " |")

    h(1, T["nor"])
    ap("")
    rows = []
    for r in KB["nor_regions"]:
        rows.append([r["name"], hexf(r["start"]), hexf(r["size"]), r["klass"],
                     "yes" if r["per_console"] else "no",
                     "yes" if r["donor_eligible"] else "no",
                     region_meaning(r, lang)])
    tbl([T["name"], T["offset"], T["size"], T["class"], T["perc"],
         T["donor"], T["meaning"]], rows)
    ap("")
    ap("[%s](index.md)" % T["back"])
    return "\n".join(A)


def build_sys(lang):
    T = L[lang]
    A = []
    ap = A.append

    def h(n, t):
        ap("#" * n + " " + t)

    def tbl(headers, rows):
        ap("| " + " | ".join(headers) + " |")
        ap("|" + "|".join(["---"] * len(headers)) + "|")
        for r in rows:
            ap("| " + " | ".join(str(c) for c in r) + " |")

    h(1, T["sys"])
    ap("")
    rows = []
    for r in KB["syscon_regions"]:
        rows.append([r["name"], hexf(r["start"]), hexf(r["size"]), r["klass"],
                     "yes" if r["per_console"] else "no",
                     "yes" if r["donor_eligible"] else "no",
                     region_meaning(r, lang)])
    tbl([T["name"], T["offset"], T["size"], T["class"], T["perc"],
         T["donor"], T["meaning"]], rows)
    ap("")
    snv = KB["snvs"]
    h(2, "NVS vs SNVS")
    ap("")
    ap("- **sc_nvs** (identity): board-id, serial, MAC, calibration - "
       "per-console, never transplant.")
    if lang == "ar":
        ap("- **sc_nvs** (الهوية): board-id والسيريال وMAC والمعايرة - خاصة "
           "بالكونسول، لا تُنقل.")
    ap("- **SNVS**: SAMU-encrypted; downgrade/replay needs hardware glitch + "
       "the console's own captured traffic.")
    if lang == "ar":
        ap("- **SNVS**: مشفّر بـ SAMU؛ الرجوع/التشغيل يحتاج glitch عتادي + "
           "مرور الكونسول الملتقط الخاص به.")
    ap("")
    ap("[%s](index.md)" % T["back"])
    return "\n".join(A)


def build_faults(lang):
    T = L[lang]
    A = []
    ap = A.append

    def h(n, t):
        ap("#" * n + " " + t)

    def tbl(headers, rows):
        ap("| " + " | ".join(headers) + " |")
        ap("|" + "|".join(["---"] * len(headers)) + "|")
        for r in rows:
            ap("| " + " | ".join(str(c) for c in r) + " |")

    h(1, T["faults"])
    ap("")
    rows = []
    for a in KB["fault_actions"]:
        rows.append([a["action"], a["bucket"], a["fixability"],
                     a["meaning_" + lang]])
    tbl([T["action"], T["bucket"], T["fix"], T["desc"]], rows)
    ap("")
    ap("[%s](index.md)" % T["back"])
    return "\n".join(A)


def build_down(lang):
    T = L[lang]
    A = []
    ap = A.append

    def h(n, t):
        ap("#" * n + " " + t)

    def tbl(headers, rows):
        ap("| " + " | ".join(headers) + " |")
        ap("|" + "|".join(["---"] * len(headers)) + "|")
        for r in rows:
            ap("| " + " | ".join(str(c) for c in r) + " |")

    ss = KB["slot_switch"]
    snv = KB["snvs"]
    h(1, T["down"])
    ap("")
    h(2, T["fam"])
    ap("")
    rows = []
    for f in ss["families"]:
        models = ", ".join("CUH-%dxx" % m for m in f["models"]) or (
            "all unmapped" if lang == "en" else "كل غير المصنّف")
        rows.append([str(f["fam"] if f["fam"] else "all"), models,
                     ss["pattern_count"], f["desc_" + lang]])
    tbl([T["fam"], "CUH", T["pat"], T["desc"]], rows)
    ap("")
    ap("> " + ss["note_" + lang])
    ap("")
    h(2, "SNVS autopatch")
    ap("")
    ap("- " + snv["records_" + lang])
    ap("- " + snv["autopatch_" + lang])
    ap("- " + snv["readiness_" + lang] + " (threshold=%d)" %
       snv["readiness_threshold"])
    ap("")
    ap("[%s](index.md)" % T["back"])
    return "\n".join(A)


def build_manual(lang):
    T = L[lang]
    A = []
    ap = A.append

    def h(n, t):
        ap("#" * n + " " + t)

    h(1, T["manual"])
    ap("")
    for i, f in enumerate(KB["surprising_facts"], 1):
        ap("%d. %s" % (i, f[lang]))
    ap("")
    ap("[%s](index.md)" % T["back"])
    return "\n".join(A)


def build_corpus(lang):
    T = L[lang]
    A = []
    ap = A.append

    def h(n, t):
        ap("#" * n + " " + t)

    h(1, T["corpus"])
    ap("")
    if lang == "en":
        ap("Help build an OPEN corpus of which faults appear on which "
           "model/FW. Use the tool's **Export report** button (or "
           "`main.export_report`) to produce a JSON file that contains NO "
           "serial, MAC or HDD data - only model, FW, health status and the "
           "list of faulty regions.")
        ap("")
        ap("Submit it to `community/corpus/` and it will be aggregated into "
           "public statistics. See `community/SCHEMA.md` for the exact format "
           "and `community/CONTRIBUTING.md` for how to contribute.")
    else:
        ap("ساعد في بناء corpus مفتوح يربط الأعطال بكل موديل/FW. استخدم زر "
           "**تصدير التقرير** في الأداة (أو `main.export_report`) لإنتاج ملف "
           "JSON لا يحتوي أي سيريال أو MAC أو بيانات قرص - فقط الموديل وFW "
           "وحالة الصحة وقائمة المناطق المعطوبة.")
        ap("")
        ap("أرسله إلى `community/corpus/` ليُجمّع في إحصاءات عامة. انظر "
           "`community/SCHEMA.md` للصيغة الدقيقة و`community/CONTRIBUTING.md` "
           "لطريقة المساهمة.")
    ap("")
    ap("[%s](index.md)" % T["back"])
    return "\n".join(A)


# --------------------------------------------------------------------------
# Single self-contained HTML (AR/EN toggle)
# --------------------------------------------------------------------------
def build_html():
    meta = KB["meta"]
    nor = KB["nor_regions"]
    sysr = KB["syscon_regions"]
    faults = KB["fault_actions"]
    ops = KB["operations"]
    facts = KB["surprising_facts"]
    ss = KB["slot_switch"]

    def reg_rows(regions):
        out = []
        for r in regions:
            out.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>"
                       "<td>%s</td><td>%s</td></tr>" % (
                r["name"], hexf(r["start"]), hexf(r["size"]), r["klass"],
                "✔" if r["per_console"] else "—",
                "✔" if r["donor_eligible"] else "—"))
        return "\n".join(out)

    def fault_rows(lang):
        out = []
        for a in faults:
            out.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                       % (a["action"], a["bucket"], a["fixability"],
                          a["meaning_" + lang]))
        return "\n".join(out)

    def op_rows(lang):
        out = []
        for o in ops:
            out.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                o["name_" + lang], o["what_" + lang], o["problem_" + lang]))
        return "\n".join(out)

    def fact_items(lang):
        return "\n".join("<li>%s</li>" % f[lang] for f in facts)

    def sections(lang):
        T = L[lang]
        return """
 <h2>%s</h2>
 <table><thead><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr></thead>
 <tbody>%s</tbody></table>

 <h2>%s</h2>
 <table><thead><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr></thead>
 <tbody>%s</tbody></table>

 <h2>%s</h2>
 <table><thead><tr><th>%s</th><th>%s</th><th>%s</th></tr></thead>
 <tbody>%s</tbody></table>

 <h2>%s</h2>
 <ul>%s</ul>

 <h2>%s</h2>
 <p>%s</p>
""" % (
            T["nor"], T["name"], T["offset"], T["size"], T["class"],
            T["perc"], T["donor"], reg_rows(nor),
            T["faults"], T["action"], T["bucket"], T["fix"], T["desc"],
            fault_rows(lang),
            T["op"], T["op"], T["what"], T["prob"], op_rows(lang),
            T["manual"], fact_items(lang),
            T["down"], ss["note_" + lang],
        )

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PS4 NOR & Syscon Open Repair KB</title>
<style>
 body{font-family:Segoe UI,system-ui,Arial,sans-serif;margin:0;background:#14141a;color:#e6e6e6}
 header{background:#1e1e26;padding:14px 20px;display:flex;align-items:center;gap:14px}
 header h1{font-size:17px;margin:0}
 button{background:#2b2b36;color:#e6e6e6;border:1px solid #3a3a48;border-radius:6px;padding:6px 12px;cursor:pointer}
 button.active{background:#4dabf7;color:#10101a;border-color:#4dabf7}
 main{max-width:980px;margin:0 auto;padding:18px}
 table{border-collapse:collapse;width:100%%;margin:10px 0;font-size:13px}
 th,td{border:1px solid #2c2c38;padding:6px 8px;text-align:left}
 th{background:#1e1e26}
 .en,.ar{display:none}
 body.lang-en .en{display:block}
 body.lang-ar .ar{display:block}
 h2{color:#4dabf7;border-bottom:1px solid #2c2c38;padding-bottom:4px}
 code{background:#0f0f13;padding:1px 5px;border-radius:4px}
 footer{color:#888;font-size:12px;padding:18px;text-align:center}
</style>
</head>
<body class="lang-en">
<header>
 <h1>PS4 NOR &amp; Syscon Open Repair KB</h1>
 <span style="flex:1"></span>
 <button id="en" class="active" onclick="setLang('en')">EN</button>
 <button id="ar" onclick="setLang('ar')">ع</button>
</header>
<main>
 <div class="en"><p>Generated from <code>PS4 NOR EASYTOOL V1</code> (by ISLAM JAMEL). Machine-readable source: <code>kb.json</code>.</p></div>
 <div class="ar"><p>مولّدة من <code>PS4 NOR EASYTOOL V1</code> (بواسطة ISLAM JAMEL). المصدر الآلي: <code>kb.json</code>.</p></div>
 <div class="en">__EN__</div>
 <div class="ar">__AR__</div>
</main>
<footer>Docs CC-BY-4.0; code MIT. Tool &amp; data by ISLAM JAMEL. Generated __GEN__.</footer>
<script>
 function setLang(l){document.body.className='lang-'+l;
   document.getElementById('en').classList.toggle('active',l==='en');
   document.getElementById('ar').classList.toggle('active',l==='ar');}
</script>
</body></html>"""
    html = (html
            .replace("__EN__", sections("en"))
            .replace("__AR__", sections("ar"))
            .replace("__GEN__", meta["generated"]))
    return html


def write_md(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text + "\n")


def main():
    for lang in ("en", "ar"):
        d = os.path.join(DOC, lang)
        write_md(os.path.join(d, "index.md"), build(lang))
        write_md(os.path.join(d, "nor-regions.md"), build_nor(lang))
        write_md(os.path.join(d, "syscon.md"), build_sys(lang))
        write_md(os.path.join(d, "faults.md"), build_faults(lang))
        write_md(os.path.join(d, "downgrade.md"), build_down(lang))
        write_md(os.path.join(d, "field-manual.md"), build_manual(lang))
        write_md(os.path.join(d, "community-corpus.md"), build_corpus(lang))
    # HTML (self-contained, AR/EN toggle)
    html = build_html()
    # Re-render fault table for AR inside HTML by post-processing:
    import re
    # Replace the english fault meaning cells with arabic for the AR toggle
    # is unnecessary: action/bucket/fixability are language-neutral; meaning
    # shown is EN. Provide AR meaning by swapping the 4th column text.
    with open(os.path.join(DOC, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("Docs written to %s (en+ar markdown + index.html)" % DOC)


if __name__ == "__main__":
    main()
