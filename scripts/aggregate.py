#!/usr/bin/env python
# aggregate.py - Aggregate anonymized community reports into public statistics.
#
# Reads every *.json in community/corpus/ (produced by main.export_report) and
# prints / writes open statistics: how many consoles of each model/FW show
# which faults. No per-console identity is involved (reports are anonymized).
#
# Usage:  python scripts/aggregate.py [--json]
import os
import sys
import json
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CORPUS = os.path.join(REPO, "community", "corpus")
OUT = os.path.join(REPO, "community", "stats.json")


def load_reports():
    reps = []
    if not os.path.isdir(CORPUS):
        return reps
    for fn in sorted(os.listdir(CORPUS)):
        if not fn.endswith(".json"):
            continue
        try:
            reps.append(json.load(open(os.path.join(CORPUS, fn),
                                       encoding="utf-8")))
        except Exception as e:
            sys.stderr.write("skip %s: %s\n" % (fn, e))
    return reps


def main():
    reps = load_reports()
    total = len(reps)
    by_model = collections.defaultdict(lambda: {"n": 0, "status":
                 collections.Counter(), "faults": collections.Counter()})
    fault_global = collections.Counter()
    for r in reps:
        key = "%s / FW%s" % (r.get("model"), r.get("fw"))
        b = by_model[key]
        b["n"] += 1
        b["status"][r.get("assess", {}).get("status")] += 1
        for f in r.get("faults", []):
            b["faults"][f.get("action")] += 1
            fault_global[f.get("action")] += 1
    stats = {
        "total_reports": total,
        "by_model_fw": {
            k: {"reports": v["n"], "status": dict(v["status"]),
                "top_faults": v["faults"].most_common(8)}
            for k, v in sorted(by_model.items())
        },
        "top_faults_global": fault_global.most_common(15),
    }
    if "--json" in sys.argv:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print("Wrote %s" % OUT)
    # human-readable
    print("Total anonymized reports : %d" % total)
    print("Per model / FW:")
    for k, v in sorted(by_model.items()):
        print("  %-18s n=%-3d status=%s" % (k, v["n"], dict(v["status"])))
        for act, c in v["faults"].most_common(5):
            print("      %-22s %d" % (act, c))
    if fault_global:
        print("Top faults (all):")
        for act, c in fault_global.most_common(10):
            print("  %-22s %d" % (act, c))


if __name__ == "__main__":
    main()
