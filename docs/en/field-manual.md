# Field manual - tribal knowledge

1. EAP_KEY is the only truly unrecoverable NOR field. On 10xx/11xx there is NO in-NOR backup at all, so a dead EAP key is permanently unrecoverable without SAMU; the only option is destructive random regen + HDD reformat.
2. Syscon NVS has ZERO in-dump redundancy (0/869 dumps show a main/backup split), so unlike NOR NVS it cannot self-repair from the same file - it only ever says 'restore from your own backup'.
3. There is a 1-byte board-id encoding offset between NOR (byte3 = 0x06) and Syscon (byte3 = 0x05); this is why the tool refuses raw NOR->Syscon seeding.
4. The SNVS population threshold (>10,000 non-blank bytes in 0x60000-0x6A000) is an empirical magic number separating revertable (~27k) from 'Not patchable' (~2.4k) consoles; borderline (~10k) is a gray area.
5. The eMMC INACTIVE bank is intentionally left alone based on MBR ground-truth; a technician comparing a 'fixed' dump may see one emc bank unchanged and think repair failed - it is by design.
6. corrupt_mismatch (EAP main vs backup differ, both non-blank) produces TWO candidate files (A_backup, B_main) rather than one fix; trial-flash to discover which copy is good.
7. s0_nvs is not one opaque blob - it is a precisely sub-addressed structure (nvs.AREAS) with a +0x3000 mirror. Most NOR 'per-console' warnings actually stem from these sub-fields; the layout map alone hides this.
8. Syscon repair restores ONLY sc_code to donor consensus; sc_nvs identity (board-id/serial/MAC/calibration) and the entire SAMU-encrypted SNVS are per-console and never transplanted.
9. NOR write order matters: always write NOR first, then Syscon, matching. Out-of-sync writes cause BLOD (CE-40947-4).
10. Two distinct NVS parsers exist: nvs.py (NOR, simple fixed offsets) vs syscon_nvs_cpp.py (faithful fail0verflow port: flat+sparse history, write-counters). The Syscon one is the authoritative SNVS reference.
11. Model->silicon mapping is hardcoded in multiple places (sce.py, fws.py, revert.py). New CUH models (e.g. 7xxx PRO) are partially covered; anything unmapped falls back to 'all 14 slot-switch patterns'.
12. fws.DEFAULT_ROOT is a hardcoded absolute path (C:\6\DONORS\fws) that diverges from main.FWS_DIR (<app>/DONORS/fws); keep donor blobs at the app-dir copy or the GUI may not see them.
13. FW number parsing strips dots and int()s them ('13.04' -> 1304) and compares numerically; mixed-width FW strings could mis-rank donors.
14. A 'healthy' dump writes NOTHING (do_repair is a no-op); a 'repairable' dump produces a fixed .bin; any 'needs-review' action is a hard stop that emits candidate(s) for trial, not a single silent fix.

[Back to index](index.md)
