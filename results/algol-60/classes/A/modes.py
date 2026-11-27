# Compare each cost and storage record with the behaviour record of the same configuration and instance, stage by stage.
import json
recs = [json.loads(l) for l in open("/Users/christopherhay/cp-roles/classes-A/algol-60/summary.jsonl")]
beh = {(r["configuration"], r["instance"]): r for r in recs if r["mode"] == "behaviour"}
def key(st):
    a = st["attempts"][-1]
    c = a["comps"][0]
    return {"attempts": len(st["attempts"]), "posed": a["posed"][0], "answers": c["answers"][0][2], "ended_by": c["answers"][0][3],
            "states": c["states"], "err": c["err"], "susp": c["susp"], "alts": c["alts"], "ops": c["ops"], "observe": a["observe"], "safety": a["safety"]}
for r in recs:
    if r["mode"] == "behaviour": continue
    b = beh[(r["configuration"], r["instance"])]
    assert len(b["stages"]) == len(r["stages"])
    for sb, sr in zip(b["stages"], r["stages"]):
        kb, kr = key(sb), key(sr)
        d = {k: (kb[k], kr[k]) for k in kb if kb[k] != kr[k]}
        print(r["configuration"], r["instance"], r["mode"], sr["stage"], "DIFF" if d else "same", d if d else "", r["faults"] or "")
