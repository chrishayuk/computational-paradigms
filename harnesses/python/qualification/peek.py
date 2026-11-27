"""Print a short summary of raw records (a qualification helper; reads only)."""
import json
import sys


def main(paths):
    for p in paths:
        r = json.load(open(p))
        print("==", p.rsplit("/", 1)[-1], "| posing", r["run"]["posing"], "| faults", r["harness_faults"], "| notes", r["notes"])
        for s in r["stages"]:
            for a in s["attempts"]:
                print("  stage", s["stage"], "attempt", a["attempt"], a["posed"]["how"], a["posed"]["reason"],
                      "continued-after-budget" if a["posed"]["continued_after_budget"] else "",
                      "| limit", a["limit_s"], "| safety", a["safety_limit"]["action"], "| exit", a["exit"],
                      "| commitments", [(c["stage"], c["value_verbatim"]) for c in a["posed"]["replayed_commitments"]])
                for c in a["computations"]:
                    st = c["steps"]
                    print("    ", c["id"], c["execution_state"]["states"], "" if c["execution_state"]["determined"] else "(undetermined)",
                          [(q["id"], [x["verbatim"] for x in q["answers"]], q["ended_by"]) for q in c["queries"]],
                          "| budget", st["budget"], "restart", st["restart_cost"], "stage", st["stage"], "to_end", st["to_end"],
                          "restated", st["restated"], "| ops", c["problem_operations"],
                          "| alts", c["alternatives"]["at_boundary"], c["alternatives"]["by_type"],
                          "| susp", c["suspended"]["at_boundary"], c["suspended"]["items"])
                    if c["execution_state"]["error_verbatim"]:
                        print("      error:", repr(c["execution_state"]["error_verbatim"][-200:]))
                print("     observe", repr(a["observe"]["raw"][:300]), "| bindings", a["observe"]["bindings"])
                print("     stdout", repr(a["stdout"][:200]), "| stderr", repr(a["stderr"][-200:]))
                if a["store"]["quantities"]:
                    print("     store", a["store"]["quantities"])
                if a["cpu_time_s"] is not None:
                    print("     cpu", a["cpu_time_s"], "rss_kb", a["max_rss_kb"])
                if a["notes"]:
                    print("     notes", a["notes"])
                if a["effects"]:
                    print("     effects", [(e["seq"], e["entry"], e["stage"], e["during_replay_of"], e["log"]) for e in a["effects"]])


if __name__ == "__main__":
    main(sys.argv[1:])
