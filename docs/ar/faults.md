# مفردات إجراءات الأعطال

| الإجراء | الحالة | القابلية للإصلاح | المعنى |
|---|---|---|---|
| ok | ok | none | المنطقة سليمة تم التحقق منها؛ لم تُعدّل. |
| blank_ok | ok | none | مساحة فارغة مقصودة (حشو). |
| per_console_ok | ok | none | منطقة خاصة بالكونسول موجودة وصالحة؛ لا يجوز تغييرها. |
| rebuilt | info | auto | أُعيد بناؤه بنيويًا من إجماع المتبرعين. |
| skipped | info | user | تم تخطّي المنطقة (باختيار المستخدم). |
| donor_repaired | repaired | donor | استُبدلت بكتلة متبرّع مطابقة (نفس HWID/FW). |
| self_backup_main | repaired | self | نُسخت النسخة الاحتياطية داخل الدمبة فوق النسخة التالفة. |
| self_main_backup | repaired | self | نُسخت النسخة الرئيسية السليمة إلى موقع النسخة الاحتياطية. |
| donor_regen | repaired | donor | أُعيد توليد CID/UNK من متبرّع بنفس معرّف اللوحة. |
| regen_random_destructive | repaired | destructive | وُلّد مفتاح EAP عشوائي؛ يتطلب مسح القرص الصلب. حل أخير. |
| ok_unverified | warning | review | غير مؤكد أنه تالف؛ تُرك كما هو مع تعليمه للمراجعة. |
| flag_unverified | warning | review | تعذّر التحقق؛ يحتاج مراجعة بشرية. |
| flag_needs_donor | warning | donor | تالف/فارغ بلا نسخة احتياطية؛ يتطلب مطابقة متبرّع. |
| flag_unknown_fw | warning | review | برنامج غير معروف في قاعدة المتبرعين. |
| flag_review | warning | review | نتيجة غامضة؛ يُنصح بالفحص اليدوي. |
| corrupt_mismatch | warning | two-candidate | النسختان الرئيسية والاحتياطية غير فارغتين ومختلفتين -> يُنتج ملفّين مرشّحين (A=احتياطي، B=رئيسي)؛ جرّب البرمجة لاكتشاف الصحيح. |
| torus_ambiguous | warning | trial | معرّف واي-فاي/بلوتوث غامض؛ تُدرج كتل مرشّحة للتجربة. |
| flag_unrecoverable | critical | unrecoverable | لا مصدر للإصلاح (منطقة خاصة فارغة / مفتاح EAP ميت بلا نسخة). توقف إجباري؛ غالبًا يحتاج أجهزة أو SAMU. |
| self_unrecoverable | critical | unrecoverable | ذاكرة Syscon NVS بلا تكرار داخلي للإصلاح الذاتي. |
| self_both_dead | critical | unrecoverable | النسختان الرئيسية والاحتياطية ميتتان. |

[العودة إلى الفهرس](index.md)
