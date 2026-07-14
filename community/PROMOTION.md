# 📣 خطة النشر — PS4 NOR EASYTOOL V1 + قاعدة المعرفة المفتوحة
# 📣 Publishing Plan — PS4 NOR EASYTOOL V1 + Open Repair KB

> **TL;DR — بالعربية:** أداة إصلاح NOR/Syscon مجانية (واجهة + سطر أوامر)، مع قاعدة معرفة ثنائية اللغة مفتوحة المصدر. المطلوب: نشرها في مجتمعات الصيانة، وجمع تقارير دمبات **لا تكشف هوية الجهاز** لبناء corpus مفيد للجميع.
> **TL;DR — English:** A free NOR/Syscon repair tool (GUI + CLI) shipped with a bilingual open knowledge base. Goal: share it with the repair community and collect **device-identity-safe** dump reports to grow a shared corpus.

---

## ✅ 0. الوضع الحالي · Current status

| البند · Item | الحالة · Status |
|---|---|
| المستودع · Repository | ✅ منشور — `github.com/ISLAMGAZA/ps4-nor-syscon-kb` |
| الإصدار · Release | ✅ `v1.0` + ملف `PS4_NOR_EASYTOOL_V1_GUI.exe` (19.9 MB) |
| التوثيق · Docs | ✅ `README.md` + `docs/` (EN/AR) + `docs/index.html` |
| لقطات الشاشة · Screenshots | ✅ 8 واجهة + 5 سطر أوامر في `screenshots/` |
| قاعدة المعرفة · KB | ✅ `kb.json` + `community/` (SCHEMA، PROMOTION، corpus) |
| أمان الرمز · Token | ⚠️ **يجب إبطال رمز GitHub فوراً** (انظر §6) |

---

## 🚀 1. قائمة ما قبل النشر · Pre-launch checklist

- [x] تحرير `about.json` (الحالة: قيد التطوير) وربطه بالأيقونة النهائية (`ICON.jpg`).
- [x] اختبار ذاتي: `nor_run_scan` يعمل، و`do_repair(confirmed=True)` لا يوقف الكتابة.
- [x] التأكد من أن الـexe يعمل على ويندوز **32-بت** بلا تثبيت.
- [x] رفع لقطات الشاشة (GUI + CLI) وإدراجها في README و docs.
- [ ] **إبطال رمز GitHub القديم** وإنشاء رمز جديد للصيانة.
- [ ] مراجة الروابط (PayPal `paypal.me/islamjamelak`، GitHub `ISLAMGAZA`) قبل النشر.

---

## 🎯 2. المنصات المستهدفة · Target platforms

| المنصة · Platform | الجمهور · Audience | المكان · Where | النوع · Post |
|---|---|---|---|
| Reddit | دولي · International | r/ps4homebrew, r/consolerepair | EN |
| Discord | دولي/عرب | سيرفرات PS4 modding/repair | EN |
| Telegram | عربي · Arabic | قنوات صيانة PS4 | AR |
| Facebook | عربي | مجموعات صيانة ألعاب/كونسول | AR |
| PSX-Place | دولي/عرب | منتدى PSX-Place | EN + AR |
| X / Twitter | عام · Public | @ISLAMGAZA + هاشتاقات | EN قصير |
| YouTube | تعليمي | وصف الفيديو/التعليق | EN + AR |

**نصيحة:** ابدأ بمنصة واحدة أو اثنتين، ثم وسّع بناءً على التفاعل.

---

## 🗓️ 3. التسلسل الزمني · Rollout sequence

1. **اليوم 0 (تم):** إنشاء المستودع + الإصدار `v1.0` + README + docs.
2. **اليوم 1:** منشور Reddit + Discord (EN) — يجلب أول مستخدمين ومختبرين.
3. **اليوم 2:** منشور Telegram + Facebook + PSX-Place (AR) — الجمهور العربي.
4. **اليوم 3–5:** منشور X/Twitter قصير + أي فيديو/شرح مختصر.
5. **مستمر:** الرد على الأسئلة، طلب تقارير dumps **لا تكشف هوية الجهاز**، تشجيع المساهمة في الـcorpus.

---

## 📝 4. المنشورات الجاهزة · Ready-to-post messages

### 🟦 English — Reddit / Discord / X

> **PS4 NOR & Syscon Open Repair KB + EASYTOOL V1** (GUI + CLI, free, MIT)
> - NOR/Syscon repair, donor-rebuild, NVS regen, safe downgrade, slot-switch.
> - Bilingual open KB (`kb.json`) + a searchable **community corpus** you can contribute to.
> - 32-bit Windows, no install.
> - Download: https://github.com/ISLAMGAZA/ps4-nor-syscon-kb/releases
>
> Still in development. Feedback, bug reports and anonymized dumps are very welcome. Thanks!

**X / Twitter (short):**
> PS4 NOR & Syscon repair, made simple. Free GUI/CLI tool + open bilingual KB. 32-bit Windows, no install.
> Download + source: https://github.com/ISLAMGAZA/ps4-nor-syscon-kb  #PS4 #repair #NOR

### 🟩 العربية — Telegram / Facebook / PSX-Place

> **أداة PS4 NOR EASYTOOL V1 + قاعدة معرفة مفتوحة للإصلاح** (عربي/إنجليزي)
> - إصلاح NOR و Syscon، بناء من متبرعين، توليد NVS، تنزيل آمن، قلب بنوك.
> - قاعدة مفتوحة قابلة للبحث يساهم فيها الجميع (`kb.json`) + زر «Submit to corpus» لإرسال تقارير **لا تكشف هوية الجهاز**.
> - ويندوز 32-بت، بلا تثبيت.
> - التحميل: https://github.com/ISLAMGAZA/ps4-nor-syscon-kb/releases
>
> المشروع لا يزال قيد التطوير. ملاحظاتكم وتقارير الأخطاء والدمبات التي لا تكشف هوية الجهاز مرحّب بها جداً. شكراً!

---

## 🤝 5. بناء قاعدة المعرفة · Growing the community corpus

- الهدف: قاعدة قابلة للبحث يساهم فيها الجميع، وتتيح للفنيّين إرسال تقارير دمبات **لا تكشف هوية الجهاز** (دون حفظ serial/MAC/بيانات شخصية).
- الطريقة: داخل التطبيق زر «Submit to corpus» يرسل تقريراً مُجرّداً فقط.
- التوثيق: `community/SCHEMA.md` يشرح شكل التقرير، و`docs/ar/community-corpus.md` يشرح الفكرة.
- **لا تطلب بيانات حسّاسة**؛ فقط تقارير لا تكشف هوية الجهاز.

---

## ⚠️ 6. ملاحظات وآداب · Do / Don't

- ✅ كن شفافاً: هذا مشروعك (قيد التطوير) — لا تدّعِ غير ذلك.
- ✅ ادعم بوضوح: رابط الدعم `paypal.me/islamjamelak` والكود من `ISLAMGAZA`.
- ✅ شجّع المساهمة في الـcorpus بأسلوب لطيف.
- ❌ **أمان:** ألغِ رمز GitHub القديم (`github_pat_11CHCI4...` و`ghp_HNxuYGO...`) فوراً من إعدادات GitHub ← Developer settings، وأنشئ رمزاً جديداً للصيانة.
- ❌ لا تطلب/تشارك بيانات تعريف الأجهزة (serial/MAC).

---

## 📊 7. مؤشرات النجاح · Success metrics

| المؤشر · Metric | المستهدف · Target |
|---|---|
| زيارات المستودع · Repo visits | نمو أسبوعي مستمر |
| تنزيلات الإصدار · Release downloads | تتجاوز 100 في أول شهر |
| تقارير corpus · Corpus reports | أول 10 تقارير خلال شهر |
| تفاعل المجتمع · Engagement | أسئلة/مساهمات على Issues/Discussions |
| نجاح إصلاحات · Repair success | ملاحظات مستخدمين بأجهزة تم إنقاذها |

---

> **توقيع المساعد · Assistant signature:** صِيغَت هذه القاعدة والمستودع بـ opencode — لأجل الأيادي التي تُصلح، لا للحاويات التي تمتلئ. كل جهاز يُعاد إحياؤه نصرٌ صغير.
> **Support:** https://paypal.me/islamjamelak · **Code/Data:** https://github.com/ISLAMGAZA
