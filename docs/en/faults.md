# Fault action vocabulary

| Action | Bucket | Fixability | Meaning |
|---|---|---|---|
| ok | ok | none | Region verified good; untouched. |
| blank_ok | ok | none | Intentionally empty padding. |
| per_console_ok | ok | none | Per-console region present and valid; must not be changed. |
| rebuilt | info | auto | Structurally rebuilt from donor consensus. |
| skipped | info | user | Region intentionally skipped (user choice). |
| donor_repaired | repaired | donor | Replaced with a matching donor blob (same HWID/FW). |
| self_backup_main | repaired | self | Copied the in-dump backup copy over the corrupted main copy. |
| self_main_backup | repaired | self | Copied the good main copy into the backup slot. |
| donor_regen | repaired | donor | Regenerated CID/UNK from a same-Board-ID donor. |
| regen_random_destructive | repaired | destructive | Generated a random EAP key; REQUIRES HDD wipe. Last resort. |
| ok_unverified | warning | review | Not provably corrupt; kept as-is, flagged for review. |
| flag_unverified | warning | review | Could not verify; needs human review. |
| flag_needs_donor | warning | donor | Corrupt/blank and no self-backup; a donor match is required. |
| flag_unknown_fw | warning | review | Firmware not recognised by the donor DB. |
| flag_review | warning | review | Ambiguous result; manual inspection advised. |
| corrupt_mismatch | warning | two-candidate | Main and backup copies both non-blank but differ -> TWO candidates emitted (A=backup, B=main); trial-flash to discover the good one. |
| torus_ambiguous | warning | trial | Wi-Fi/BT firmware HWID ambiguous; candidate blobs listed to trial-flash. |
| flag_unrecoverable | critical | unrecoverable | No source to repair from (blank per-console / dead EAP key with no backup). Hard stop; often needs hardware or SAMU. |
| self_unrecoverable | critical | unrecoverable | Syscon NVS has no in-dump redundancy to self-repair from. |
| self_both_dead | critical | unrecoverable | Both main and backup copies are dead. |

[Back to index](index.md)
