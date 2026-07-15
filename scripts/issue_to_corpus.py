#!/usr/bin/env python
# issue_to_corpus.py - Convert a "Submit an anonymized dump report" issue into
# a corpus JSON file.
#
# Reads the issue body from the ISSUE_BODY env var (or --body-file), extracts
# the pasted JSON, validates the schema and the anonymization guard, and writes
# community/corpus/<name>.json. On success it prints the written path to stdout
# and writes key=value outputs to $GITHUB_OUTPUT (status, path, message).
#
# Exit code is always 0; the "status" output is "ok" or "rejected" so the
# workflow can comment appropriately.
import os
import re
import sys
import json
import hashlib
import argparse
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CORPUS = os.path.join(REPO, "community", "corpus")

# Fields we allow to persist in a corpus report. Anything else is dropped.
ALLOWED_TOP = {
    "schema", "tool", "sub", "model", "sku", "fw", "assess", "faults",
    "regions", "donor_available", "fingerprint_sha256", "generated",
}
# Substrings that must never appear anywhere in a submitted report.
FORBIDDEN_KEYS = (
    "serial", "serialno", "serial_no", "mac", "macaddr", "mac_address",
    "board_id", "boardid", "board-id", "hdd", "psid", "openpsid", "idps",
    "moniker", "console_id", "consoleid",
)
# Value patterns that look like real identifiers.
RE_MAC = re.compile(r"\b(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b")
RE_SERIAL = re.compile(r"\b[A-Z]{2}\d{13,}\b")
RE_LONGHEX = re.compile(r"\b[0-9a-fA-F]{32,}\b")


def set_output(**kw):
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        for k, v in kw.items():
            if "\n" in str(v):
                f.write("%s<<__EOF__\n%s\n__EOF__\n" % (k, v))
            else:
                f.write("%s=%s\n" % (k, v))


def extract_json(body):
    """Pull the JSON blob out of a GitHub issue-form body."""
    # Prefer a fenced ```json ... ``` block.
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", body, re.S)
    if m:
        return m.group(1)
    # Otherwise take the section under the "report" textarea heading.
    m = re.search(r"(?is)###\s*Paste the anonymized JSON report\s*(.+?)"
                  r"(?:\n###\s|\Z)", body)
    chunk = m.group(1) if m else body
    # Grab the outermost {...}.
    start = chunk.find("{")
    end = chunk.rfind("}")
    if start != -1 and end != -1 and end > start:
        return chunk[start:end + 1]
    return None


def guard(rep, raw):
    for k in FORBIDDEN_KEYS:
        if k in raw.lower():
            return "raw report contains forbidden token '%s'" % k
    if RE_MAC.search(raw):
        return "raw report contains a MAC-address-like value"
    if RE_SERIAL.search(raw):
        return "raw report contains a serial-number-like value"
    # long hex is only allowed for the fingerprint field
    for m in RE_LONGHEX.finditer(raw):
        val = m.group(0)
        if val != (rep.get("fingerprint_sha256") or ""):
            return "raw report contains an unexpected long hex value"
    return None


def validate(rep):
    if not isinstance(rep, dict):
        return "top-level JSON is not an object"
    if rep.get("tool") != "PS4 NOR EASYTOOL V1":
        return "missing/incorrect 'tool' field"
    if rep.get("sub") not in ("nor", "syscon"):
        return "'sub' must be 'nor' or 'syscon'"
    if not isinstance(rep.get("assess"), dict):
        return "missing 'assess' object"
    if not isinstance(rep.get("faults"), list):
        return "missing 'faults' list"
    if not isinstance(rep.get("regions"), list):
        return "missing 'regions' list"
    return None


def content_sig(rep):
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
    blob = json.dumps(key, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def safe_name(rep, sig):
    model = rep.get("model")
    fw = rep.get("fw")
    model = "m%s" % model if model is not None else "mNA"
    fw = "fw%s" % fw if fw else "fwNA"
    return "%s-%s-%s-%s.json" % (rep.get("sub"), model, fw, sig[:12])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--body-file")
    args = ap.parse_args()

    if args.body_file:
        with open(args.body_file, encoding="utf-8") as f:
            body = f.read()
    else:
        body = os.environ.get("ISSUE_BODY", "")

    def reject(msg):
        print("REJECTED: %s" % msg, file=sys.stderr)
        set_output(status="rejected", message=msg)
        sys.exit(0)

    raw = extract_json(body)
    if not raw:
        reject("could not find a JSON report in the issue body")
    try:
        rep = json.loads(raw)
    except Exception as e:
        reject("the pasted report is not valid JSON: %s" % e)

    err = validate(rep)
    if err:
        reject(err)
    err = guard(rep, raw)
    if err:
        reject("anonymization guard: %s" % err)

    rep = {k: v for k, v in rep.items() if k in ALLOWED_TOP}
    rep.setdefault("schema", "1.0")
    rep.setdefault("generated", datetime.datetime.now(datetime.timezone.utc)
                   .strftime("%Y-%m-%dT%H:%M:%SZ"))

    sig = content_sig(rep)
    name = safe_name(rep, sig)
    os.makedirs(CORPUS, exist_ok=True)
    dest = os.path.join(CORPUS, name)
    if os.path.exists(dest):
        set_output(status="duplicate", path="community/corpus/%s" % name,
                   message="This exact profile is already in the corpus "
                           "(%s). Thanks anyway!" % name)
        print("DUPLICATE: %s" % name)
        return
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    set_output(status="ok", path="community/corpus/%s" % name, name=name,
               message="Added `community/corpus/%s` to the corpus." % name)
    print("WROTE: %s" % dest)


if __name__ == "__main__":
    main()
