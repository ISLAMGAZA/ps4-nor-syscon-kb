#!/usr/bin/env python
# seed_corpus.py - Bootstrap the community corpus with anonymized reports.
#
# Runs LOCALLY only. Reads real donor dumps from a DONORS folder, produces
# ANONYMIZED health reports (no serial / MAC / HDD / board-id) via
# main.export_report(), and writes them into community/corpus/.
#
# The raw dumps are NEVER copied or uploaded - only the anonymized JSON.
#
# Usage:
#   python scripts/seed_corpus.py --donors C:\6\DONORS --nor 100 --syscon 100
#
import os
import sys
import glob
import random
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CORPUS = os.path.join(REPO, "community", "corpus")


def _find_engine():
    """Locate the ps4repair package so we can import main.export_report."""
    for cand in (
        os.path.join(os.path.dirname(REPO), "ps4repair"),
        os.path.join(REPO, "ps4repair"),
        r"C:\6\ps4repair",
    ):
        if os.path.isdir(cand):
            return cand
    return None


def collect(donors, sub):
    if sub == "nor":
        size = 0x2000000
        subdirs = ["NORDONORS", "nor", "NOR"]
    else:
        size = 0x80000
        subdirs = ["syscon_donors", "syscon", "SYSCON"]
    roots = [os.path.join(donors, d) for d in subdirs]
    roots.append(donors)
    seen = set()
    out = []
    for r in roots:
        if not os.path.isdir(r):
            continue
        for p in glob.glob(os.path.join(r, "**", "*"), recursive=True):
            if not os.path.isfile(p):
                continue
            ap = os.path.abspath(p)
            if ap in seen:
                continue
            try:
                if os.path.getsize(ap) != size:
                    continue
            except OSError:
                continue
            seen.add(ap)
            out.append(ap)
    return out


def build_report(engine_main, path, sub):
    """Fast anonymized report (allow_donor=False to skip slow donor search).

    Mirrors main.export_report output shape but is ~200x faster because it
    does not scan the 600+ donor library for every region.
    """
    import io
    import hashlib
    import datetime
    import ui as _ui
    _saved = {n: getattr(_ui, n) for n in
              ("info", "ok", "warn", "err", "title", "hr",
               "menu_item", "clear", "kv", "banner")}
    for n in _saved:
        setattr(_ui, n, lambda *a, **k: None)
    old = sys.stdout
    sys.stdout = io.StringIO()
    try:
        if sub == "syscon":
            res = engine_main.syscon_run_scan(path, allow_donor=False,
                                              strict=False)
        else:
            res = engine_main.run_scan(path, allow_donor=False, strict=False)
        assess = engine_main.quick_assess(path, sub)
    finally:
        sys.stdout = old
        for n, f in _saved.items():
            setattr(_ui, n, f)
    res = res or {}
    summary = res.get("summary") or {}
    fp = res.get("fingerprint") or ""
    faults = engine_main.faults_from(res)
    acts = res.get("actions") or []
    regions = [{"region": a.get("region"), "category": a.get("category"),
                "status": a.get("action")} for a in acts]
    return {
        "schema": getattr(engine_main, "EXPORT_SCHEMA", "1.0"),
        "tool": "PS4 NOR EASYTOOL V1",
        "sub": sub,
        "model": summary.get("model"),
        "sku": summary.get("sku"),
        "fw": summary.get("fw"),
        "assess": {
            "status": assess.get("status"),
            "counts": assess.get("counts"),
            "changes": assess.get("changes"),
        },
        "faults": faults,
        "regions": regions,
        "donor_available": None,
        "fingerprint_sha256": (hashlib.sha256(
            fp.encode("utf-8", "ignore")).hexdigest()
            if isinstance(fp, str) and fp else None),
        "generated": datetime.datetime.now(datetime.timezone.utc)
                          .strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def content_sig(rep):
    """Stable signature of a report's meaningful content (identity-free)."""
    import json as _j
    import hashlib
    key = {
        "sub": rep.get("sub"),
        "model": rep.get("model"),
        "fw": rep.get("fw"),
        "status": (rep.get("assess") or {}).get("status"),
        "faults": sorted((f.get("region"), f.get("action"))
                         for f in rep.get("faults", [])),
        "regions": sorted((r.get("region"), r.get("status"))
                          for r in rep.get("regions", [])),
    }
    blob = _j.dumps(key, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def safe_name(rep, sub, sig):
    model = rep.get("model")
    fw = rep.get("fw")
    model = "m%s" % model if model is not None else "mNA"
    fw = "fw%s" % fw if fw else "fwNA"
    return "%s-%s-%s-%s.json" % (sub, model, fw, sig[:12])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--donors", default=r"C:\6\DONORS")
    ap.add_argument("--nor", type=int, default=100)
    ap.add_argument("--syscon", type=int, default=100)
    ap.add_argument("--scan-limit", type=int, default=0,
                    help="max dumps to SCAN per subsystem (0 = all)")
    ap.add_argument("--only", choices=["nor", "syscon"], default=None)
    ap.add_argument("--seed", type=int, default=1337)
    args = ap.parse_args()

    engine = _find_engine()
    if not engine:
        sys.exit("Could not find the ps4repair package (engine).")
    sys.path.insert(0, engine)
    os.makedirs(CORPUS, exist_ok=True)
    random.seed(args.seed)

    import main as engine_main

    existing = {f for f in os.listdir(CORPUS) if f.endswith(".json")}
    seen_sig = set()
    written = 0

    for sub, want in (("nor", args.nor), ("syscon", args.syscon)):
        if args.only and sub != args.only:
            continue
        pool = collect(args.donors, sub)
        random.shuffle(pool)
        if args.scan_limit and len(pool) > args.scan_limit:
            pool = pool[:args.scan_limit]
        print("[%s] found donors, scanning %d, keeping up to %d distinct"
              % (sub, len(pool), want), flush=True)
        picked = 0
        scanned = 0
        for path in pool:
            if picked >= want:
                break
            scanned += 1
            if scanned % 50 == 0:
                print("  [%s] scanned %d, kept %d" % (sub, scanned, picked),
                      flush=True)
            try:
                rep = build_report(engine_main, path, sub)
            except Exception as e:
                sys.stderr.write("skip %s: %r\n"
                                 % (os.path.basename(path), e))
                continue
            sig = content_sig(rep)
            if sig in seen_sig:
                continue
            seen_sig.add(sig)
            name = safe_name(rep, sub, sig)
            if name in existing:
                continue
            existing.add(name)
            import json as _j
            with open(os.path.join(CORPUS, name), "w", encoding="utf-8") as f:
                _j.dump(rep, f, ensure_ascii=False, indent=2)
            written += 1
            picked += 1
            if picked % 20 == 0:
                print("  [%s] %d/%d" % (sub, picked, want), flush=True)
        print("[%s] wrote %d reports" % (sub, picked))

    print("Done. %d new corpus reports in %s" % (written, CORPUS))


if __name__ == "__main__":
    main()
