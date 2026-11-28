"""Summarise the raw records of P11 and P12 (python), one line per stage.

Reads only results/python/<configuration>/{P11,P12}/raw/*.json(.gz).
Usage: python3 summarize.py REPO_ROOT [mode]
"""
import glob
import gzip
import json
import os
import sys

root = sys.argv[1]
modes = sys.argv[2:] or ["behaviour"]


def load(p):
    if p.endswith(".gz"):
        with gzip.open(p, "rt") as f:
            return json.load(f)
    with open(p) as f:
        return json.load(f)


rows = []
for conf in ("core", "stdlib-concurrency", "extended"):
    for prob in ("P11", "P12"):
        for p in sorted(glob.glob(os.path.join(root, "results/python", conf, prob, "raw*", "*.json"))) + sorted(glob.glob(os.path.join(root, "results/python", conf, prob, "raw*", "*.json.gz"))):
            r = load(p)
            run = r["run"]
            if run["mode"] not in modes:
                continue
            for st in r["stages"]:
                for a in st["attempts"]:
                    for c in a["computations"]:
                        ans = [x["verbatim"] for q in c["queries"] for x in q["answers"]]
                        ended = [q["ended_by"] for q in c["queries"]]
                        s = c["steps"]
                        print("|".join(str(v) for v in [
                            conf, run["instance"], run["mode"], os.path.relpath(p, root), "stage", st["stage"],
                            "att", a["attempt"], a["posed"]["how"], a["posed"]["reason"],
                            "replayed_commit", a["posed"].get("replayed_commitments"),
                            "ans", ans, ended, "state", c["execution_state"]["states"],
                            "steps", s.get("stage"), s.get("restated"), s.get("to_first_answer"),
                            s.get("between_answers") if s.get("between_answers") is None or len(s.get("between_answers")) < 6 else ("len", len(s["between_answers"])),
                            s.get("budget_exhausted"),
                            "alt", c["alternatives"].get("at_boundary"), c["alternatives"].get("by_type"),
                            "pdalt", c["alternatives"].get("problem_defined"),
                            "susp", c["suspended"].get("at_boundary"),
                            "ops", c.get("problem_operations"), "cand", c.get("candidates_examined"),
                            "eff", [(e["seq"], e["entry"], e["stage"], e["during_replay_of"], e["log"]) for e in (a.get("effects") or [])],
                            "obs", a["observe"]["raw"].replace("\n", " / ")[:400],
                            "stdout_len", len(a["stdout"] or ""), "stderr", (a["stderr"] or "")[:200],
                            "safety", a["safety_limit"]["action"], "manual", a.get("manual_actions"),
                            "store", {k: (v.get("boundary"), v.get("peak")) for k, v in (a["store"].get("quantities") or {}).items()},
                        ]))
            print("RECORD|", os.path.relpath(p, root), "faults", r.get("harness_faults"), "notes", r.get("notes"),
                  "manual", r.get("manual_actions"),
                  "effects_after", None if not r.get("effects") else [(e["seq"], e["entry"], e["run_id"][-17:], e["stage"]) for e in r["effects"]["log_after_run"]],
                  "before", None if not r.get("effects") else r["effects"]["entries_before_run"])
