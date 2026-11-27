#!/usr/bin/env python3
"""Check raw run records against harnesses/record.schema.json and the rules
of harnesses/README.md ("The raw record", "Rules a record must keep").

    validate.py [--schema FILE] [--stages FILE] RECORD.json ...
    validate.py --check-stages [FILE]

Python 3 standard library only. Exit status: 0 if every file is valid,
1 if any is not, 2 on a usage error or an unreadable schema.

The schema check implements the subset of JSON Schema (2020-12) that
record.schema.json uses: type, enum, const, properties, required,
additionalProperties, items, minItems, maxItems, uniqueItems, minimum,
exclusiveMinimum, minLength, pattern, oneOf, anyOf and local $ref.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SCHEMA = os.path.join(HERE, "record.schema.json")
DEFAULT_STAGES = os.path.join(HERE, "stages.json")

EXEC_STATES = {"finished", "alternatives pending", "suspended", "budget", "timeout", "error"}
TERMINAL = {"budget", "timeout", "error"}


# ---------------------------------------------------------------- schema ---

class Schema:
    def __init__(self, root):
        self.root = root

    def resolve(self, ref):
        if not ref.startswith("#/"):
            raise ValueError("only local $ref is supported: %r" % ref)
        node = self.root
        for part in ref[2:].split("/"):
            node = node[part]
        return node

    def errors(self, inst, schema, path="$"):
        """Return a list of error strings for inst against schema."""
        out = []
        if "$ref" in schema:
            out += self.errors(inst, self.resolve(schema["$ref"]), path)
        if "type" in schema and not type_ok(inst, schema["type"]):
            return out + ["%s: expected %s, got %s" % (path, schema["type"], json_type(inst))]
        if "const" in schema and not same(inst, schema["const"]):
            out.append("%s: must be %r" % (path, schema["const"]))
        if "enum" in schema and not any(same(inst, e) for e in schema["enum"]):
            out.append("%s: %r is not one of %r" % (path, inst, schema["enum"]))
        if isinstance(inst, str):
            if "minLength" in schema and len(inst) < schema["minLength"]:
                out.append("%s: shorter than %d" % (path, schema["minLength"]))
            if "pattern" in schema and not re.search(schema["pattern"], inst):
                out.append("%s: %r does not match %s" % (path, inst, schema["pattern"]))
        if is_number(inst):
            if "minimum" in schema and inst < schema["minimum"]:
                out.append("%s: %r is below %r" % (path, inst, schema["minimum"]))
            if "exclusiveMinimum" in schema and inst <= schema["exclusiveMinimum"]:
                out.append("%s: %r is not above %r" % (path, inst, schema["exclusiveMinimum"]))
        if isinstance(inst, list):
            if "minItems" in schema and len(inst) < schema["minItems"]:
                out.append("%s: fewer than %d items" % (path, schema["minItems"]))
            if "maxItems" in schema and len(inst) > schema["maxItems"]:
                out.append("%s: more than %d items" % (path, schema["maxItems"]))
            if schema.get("uniqueItems"):
                seen = []
                for x in inst:
                    if any(same(x, y) for y in seen):
                        out.append("%s: duplicate item %r" % (path, x))
                    seen.append(x)
            if "items" in schema:
                for i, x in enumerate(inst):
                    out += self.errors(x, schema["items"], "%s[%d]" % (path, i))
        if isinstance(inst, dict):
            for key in schema.get("required", []):
                if key not in inst:
                    out.append("%s: missing required %r" % (path, key))
            props = schema.get("properties", {})
            for key, val in inst.items():
                if key in props:
                    out += self.errors(val, props[key], "%s.%s" % (path, key))
                else:
                    extra = schema.get("additionalProperties", True)
                    if extra is False:
                        out.append("%s: unexpected property %r" % (path, key))
                    elif isinstance(extra, dict):
                        out += self.errors(val, extra, "%s.%s" % (path, key))
        if "oneOf" in schema:
            results = [self.errors(inst, s, path) for s in schema["oneOf"]]
            ok = [r for r in results if not r]
            if len(ok) != 1:
                if not ok:
                    best = min(results, key=len)
                    out.append("%s: matches none of oneOf; nearest: %s" % (path, "; ".join(best[:3])))
                else:
                    out.append("%s: matches %d alternatives of oneOf, not exactly one" % (path, len(ok)))
        if "anyOf" in schema:
            results = [self.errors(inst, s, path) for s in schema["anyOf"]]
            if all(results):
                best = min(results, key=len)
                out.append("%s: matches none of anyOf; nearest: %s" % (path, "; ".join(best[:3])))
        return out


def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def json_type(x):
    if x is None:
        return "null"
    if isinstance(x, bool):
        return "boolean"
    if isinstance(x, int):
        return "integer"
    if isinstance(x, float):
        return "number"
    if isinstance(x, str):
        return "string"
    if isinstance(x, list):
        return "array"
    if isinstance(x, dict):
        return "object"
    return type(x).__name__


def type_ok(x, t):
    if isinstance(t, list):
        return any(type_ok(x, u) for u in t)
    j = json_type(x)
    if t == "number":
        return j in ("integer", "number")
    if t == "integer" and j == "number":
        return float(x).is_integer()
    return j == t


def same(a, b):
    """JSON equality: 1 == 1.0, but True != 1."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    return a == b


# ---------------------------------------------------------------- stages ---

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def index_stages(stages_doc):
    """instance id -> (problem entry, subproblem entry, instance entry)."""
    idx = {}
    for prob in stages_doc.get("problems", []):
        for sub in prob.get("subproblems", []):
            for inst in sub.get("instances", []):
                idx[inst["id"]] = (prob, sub, inst)
    return idx


def problem_limits(stages_doc, prob):
    lim = dict(stages_doc.get("default_limits", {}))
    lim.update(prob.get("limits", {}))
    return lim


def query_cap(q, inst):
    if q.get("cap") is not None:
        return q["cap"]
    return inst.get("parameters", {}).get("cap")


def check_stages_doc(doc):
    """Structural checks of a stages file. Returns a list of errors."""
    errs = []
    if doc.get("format") != "cp-stages/1":
        errs.append("format must be cp-stages/1")
    seen_inst, seen_sub = set(), set()
    for prob in doc.get("problems", []):
        pid = prob.get("problem", "?")
        if not re.match(r"^(P(0[1-9]|1[0-6])|X[0-9]{2})$", pid):
            errs.append("%s: bad problem id" % pid)
        if not isinstance(prob.get("effects"), bool):
            errs.append("%s: 'effects' must be true or false" % pid)
        lim = problem_limits(doc, prob)
        for key in ("budget_steps", "safety_limit_s", "rerun_limit_s"):
            if key not in lim:
                errs.append("%s: limits lack %s" % (pid, key))
        for sub in prob.get("subproblems", []):
            sid = sub.get("id", "?")
            where = "%s/%s" % (pid, sid)
            if sid in seen_sub:
                errs.append("%s: duplicate sub-problem id" % where)
            seen_sub.add(sid)
            if not sid.startswith(pid):
                errs.append("%s: sub-problem id does not start with its problem id" % where)
            if not (isinstance(sub.get("line"), int) and sub["line"] >= 1):
                errs.append("%s: line must be a positive integer" % where)
            insts = sub.get("instances", [])
            if not insts:
                errs.append("%s: no instances" % where)
            for inst in insts:
                if inst["id"] in seen_inst:
                    errs.append("%s: duplicate instance id %s" % (where, inst["id"]))
                seen_inst.add(inst["id"])
                if not inst["id"].startswith(sid):
                    errs.append("%s: instance %s does not start with its sub-problem id" % (where, inst["id"]))
                p = inst.get("parameters", {})
                if "answers" in p or "cap" in p:
                    if {"all": 20, "any-one": 1}.get(p.get("answers")) != p.get("cap"):
                        errs.append("%s: instance %s: answers and cap disagree" % (where, inst["id"]))
            stages = sub.get("stages", [])
            if [s.get("stage") for s in stages] != list(range(1, len(stages) + 1)):
                errs.append("%s: stages are not numbered 1..%d" % (where, len(stages)))
            for st in stages:
                sw = "%s stage %s" % (where, st.get("stage"))
                for key in ("line", "kind", "description", "queries", "commit", "spawns"):
                    if key not in st:
                        errs.append("%s: lacks %s" % (sw, key))
                if not (isinstance(st.get("line"), int) and st["line"] >= 1):
                    errs.append("%s: line must be a positive integer" % sw)
                if st.get("kind") not in doc.get("vocabulary", {}).get("kind", {}):
                    errs.append("%s: unknown kind %r" % (sw, st.get("kind")))
                if (st.get("kind") == "commit") != bool(st.get("commit")):
                    errs.append("%s: kind 'commit' and commit: true must go together" % sw)
                if st.get("commit") and not prob.get("effects"):
                    errs.append("%s: a commit stage in a problem without effects" % sw)
                if not st.get("queries"):
                    errs.append("%s: no queries" % sw)
                comps = set()
                for q in st.get("queries", []):
                    comps.add(q.get("computation"))
                    ans, cap = q.get("answers"), q.get("cap")
                    if ans is None or cap is None:
                        if not (ans is None and cap is None):
                            errs.append("%s: query %s: answers and cap must both be null or both set" % (sw, q.get("id")))
                        for inst in insts:
                            if query_cap(q, inst) not in (1, 20):
                                errs.append("%s: query %s: instance %s gives no cap" % (sw, q.get("id"), inst["id"]))
                    elif {"all": 20, "any-one": 1}.get(ans) != cap:
                        errs.append("%s: query %s: answers %r with cap %r" % (sw, q.get("id"), ans, cap))
                spawns = st.get("spawns", [])
                if spawns:
                    if set(spawns) != comps:
                        errs.append("%s: spawned computations %r are not the queries' computations %r" % (sw, spawns, sorted(comps)))
                    for inst in insts:
                        order = inst.get("parameters", {}).get("spawn_order")
                        if order is not None and sorted(order) != sorted(spawns):
                            errs.append("%s: instance %s spawn_order %r does not match spawns" % (sw, inst["id"], order))
                elif comps != {"main"}:
                    errs.append("%s: queries on computations %r but nothing is spawned" % (sw, sorted(comps)))
                if "spawn_fallback" in st and not st.get("fallback_queries"):
                    errs.append("%s: spawn_fallback without fallback_queries" % sw)
    return errs


# --------------------------------------------------------------- records ---

def final_attempt(stage):
    return stage["attempts"][-1]


def check_record(rec, stages_doc, path):
    """Rules beyond the schema. Returns (errors, warnings)."""
    E, W = [], []
    run = rec["run"]
    mode = run["mode"]
    lim = run["limits"]
    stages = rec["stages"]
    K = len(stages)

    if rec.get("made_up"):
        W.append("this record is MADE UP (made_up: true); it is a test of validate.py, not a result")
    elif run.get("purpose") == "example":
        E.append("run.purpose is 'example' but made_up is not true")

    stem = os.path.splitext(os.path.basename(path))[0]
    if stem != run["run_id"]:
        W.append("file name %r is not run_id %r + '.json'" % (os.path.basename(path), run["run_id"]))

    # --- cross-check against stages.json
    idx = index_stages(stages_doc)
    spec = idx.get(run["instance"])
    if spec is None:
        E.append("instance %r is not in the stages file" % run["instance"])
    else:
        prob, sub, inst = spec
        if prob["problem"] != run["problem"]:
            E.append("instance %s belongs to %s, not %s" % (run["instance"], prob["problem"], run["problem"]))
        if sub["id"] != run["subproblem"]:
            E.append("instance %s belongs to %s, not %s" % (run["instance"], sub["id"], run["subproblem"]))
        if not same_params(run["parameters"], inst.get("parameters", {})):
            E.append("run.parameters %r differ from the instance's %r" % (run["parameters"], inst.get("parameters", {})))
        plim = problem_limits(stages_doc, prob)
        if lim["budget_steps"] != plim["budget_steps"]:
            E.append("budget_steps %r, the problem's is %r" % (lim["budget_steps"], plim["budget_steps"]))
        if lim["safety_limit_s"] != plim["safety_limit_s"]:
            E.append("safety_limit_s %r, the problem's is %r" % (lim["safety_limit_s"], plim["safety_limit_s"]))
        if lim["rerun_limit_s"] != plim["rerun_limit_s"]:
            E.append("rerun_limit_s %r, the problem's is %r" % (lim["rerun_limit_s"], plim["rerun_limit_s"]))
        spec_stages = sub["stages"]
        if run["complete"] and K != len(spec_stages):
            E.append("run.complete but %d stages recorded, the instance has %d" % (K, len(spec_stages)))
        if K > len(spec_stages):
            E.append("%d stages recorded, the instance has only %d" % (K, len(spec_stages)))
        if not run["complete"] and not run.get("incomplete_reason"):
            E.append("run.complete is false and no incomplete_reason is given")
        if prob.get("effects") and rec["effects"] is None:
            E.append("%s has effects; record.effects must not be null" % prob["problem"])
        if not prob.get("effects") and rec["effects"] is not None:
            E.append("%s has no effects; record.effects must be null" % prob["problem"])
        commit_stages = [s["stage"] for s in spec_stages if s.get("commit")]
        for st in stages:
            k = st["stage"]
            if k > len(spec_stages):
                continue
            sst = spec_stages[k - 1]
            for a in st["attempts"]:
                where = "stage %d attempt %d" % (k, a["attempt"])
                check_queries_against_spec(a, sst, inst, where, E)
                rc = [c["stage"] for c in a["posed"]["replayed_commitments"]]
                for c in rc:
                    if c not in commit_stages or c >= k:
                        E.append("%s: replayed commitment for stage %d, which is not an earlier commit stage" % (where, c))
                if a["posed"]["how"] == "reposed":
                    for c in commit_stages:
                        if c < k and c not in rc:
                            W.append("%s: reposed past commit stage %d with no replayed commitment (the system selected nothing?)" % (where, c))

    # --- stage numbering
    if [s["stage"] for s in stages] != list(range(1, K + 1)):
        E.append("stages are not numbered 1..%d in order" % K)

    prev_final = None
    for st in stages:
        k = st["stage"]
        atts = st["attempts"]
        if [a["attempt"] for a in atts] != list(range(1, len(atts) + 1)):
            E.append("stage %d: attempts are not numbered 1, 2" % k)
        for a in atts:
            where = "stage %d attempt %d" % (k, a["attempt"])
            check_attempt(rec, run, k, a, len(atts), prev_final, where, E, W)
        prev_final = final_attempt(st)
    return E, W


def same_params(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def check_queries_against_spec(a, sst, inst, where, E):
    comps = {c["id"]: c for c in a["computations"]}
    spawns = sst.get("spawns", [])
    fallback = sst.get("spawn_fallback")
    queries = sst["queries"]
    if spawns:
        spawned = sorted(c["id"] for c in a["computations"] if c["spawned"])
        if fallback and set(comps) == {fallback} and not spawned:
            queries = sst.get("fallback_queries", queries)
        elif spawned != sorted(spawns):
            E.append("%s: spawned %r, the stage spawns %r" % (where, spawned, sorted(spawns)))
        order = inst.get("parameters", {}).get("spawn_order")
        if order and not (fallback and set(comps) == {fallback}):
            got = [c["id"] for c in sorted((c for c in a["computations"] if c["spawned"]),
                                           key=lambda c: (c.get("spawn_index") is None, c.get("spawn_index") or 0))]
            if got != order:
                E.append("%s: spawn order %r, the instance's is %r" % (where, got, order))
    else:
        if any(c["spawned"] for c in a["computations"]):
            E.append("%s: a computation is spawned in a stage that spawns none" % where)
    for q in queries:
        comp = comps.get(q["computation"])
        if comp is None:
            E.append("%s: no computation %r for query %r" % (where, q["computation"], q["id"]))
            continue
        rq = [x for x in comp["queries"] if x["id"] == q["id"]]
        if len(rq) != 1:
            E.append("%s: computation %r must record query %r exactly once" % (where, q["computation"], q["id"]))
            continue
        cap = query_cap(q, inst)
        if rq[0]["cap"] != cap:
            E.append("%s: query %r has cap %r, the problem's is %r" % (where, q["id"], rq[0]["cap"], cap))


def check_attempt(rec, run, k, a, n_attempts, prev_final, where, E, W):
    lim = run["limits"]
    mode = run["mode"]
    n = a["attempt"]

    # --- safety limit and reruns
    sl = a["safety_limit"]
    expect_limit = lim["safety_limit_s"] if n == 1 else lim["rerun_limit_s"]
    if expect_limit is None:
        E.append("%s: a rerun, but the problem fixes its safety limit (rerun_limit_s is null)" % where)
    elif a["limit_s"] != expect_limit:
        E.append("%s: limit_s %r, expected %r" % (where, a["limit_s"], expect_limit))
    if not sl["hit"] and sl["action"] != "none":
        E.append("%s: safety limit not hit, action must be 'none'" % where)
    if sl["hit"]:
        if n == 1 and lim["rerun_limit_s"] is not None and sl["action"] != "rerun":
            E.append("%s: safety limit hit on the first attempt: action must be 'rerun'" % where)
        if n == 1 and lim["rerun_limit_s"] is None and sl["action"] != "fixed-limit-timeout":
            E.append("%s: safety limit hit under a fixed limit: action must be 'fixed-limit-timeout'" % where)
        if n == 2 and sl["action"] != "final-timeout":
            E.append("%s: safety limit hit on the rerun: action must be 'final-timeout'" % where)
    if sl["action"] == "rerun" and n_attempts != 2:
        E.append("%s: action 'rerun' but no second attempt is recorded" % where)
    if n == 2 and n_attempts == 2:
        pass
    if n == 1 and n_attempts == 2 and not sl["hit"]:
        E.append("%s: a second attempt without the safety limit stopping the first" % where)

    # --- posing
    p = a["posed"]
    how, reason, replayed = p["how"], p["reason"], p["replayed"]
    if k == 1:
        if how != "fresh" or replayed:
            E.append("%s: stage 1 is posed fresh, with nothing replayed" % where)
        if n == 1 and reason != "first-stage":
            E.append("%s: stage 1, first attempt: reason must be 'first-stage'" % where)
    else:
        if how == "fresh":
            E.append("%s: only stage 1 is posed fresh" % where)
        if how == "reposed" and replayed != list(range(1, k)):
            E.append("%s: a reposed stage %d replays exactly stages 1..%d, got %r" % (where, k, k - 1, replayed))
        if how == "incremental" and replayed:
            E.append("%s: an incremental stage replays nothing" % where)
        if how == "incremental" and run["posing"] == "reposed" and not p["continued_after_budget"]:
            E.append("%s: incremental posing in a configuration that reposes" % where)
    if n == 2 and reason != "safety-rerun":
        E.append("%s: a rerun's reason must be 'safety-rerun'" % where)
    if n == 2 and k > 1 and how != "reposed":
        W.append("%s: a rerun after a safety-limit stop is normally reposed (the stopped computation is gone)" % where)
    if p["continued_after_budget"]:
        if how != "incremental":
            E.append("%s: continued_after_budget needs incremental posing" % where)
        if prev_final is None or not any("budget" in c["execution_state"]["states"] for c in prev_final["computations"]):
            E.append("%s: continued_after_budget but the previous stage did not end in budget" % where)
    if prev_final is not None and n == 1:
        prev_states = set()
        for c in prev_final["computations"]:
            prev_states |= set(c["execution_state"]["states"])
        if "error" in prev_states and how != "reposed":
            E.append("%s: after an error, the next stage is posed by reposing (PROTOCOL.md, Running)" % where)
        if "error" in prev_states and reason != "after-error":
            W.append("%s: previous stage ended in error; reason should be 'after-error'" % where)
        if reason == "after-error" and "error" not in prev_states:
            E.append("%s: reason 'after-error' but the previous stage did not end in error" % where)
        if reason == "after-budget" and "budget" not in prev_states:
            E.append("%s: reason 'after-budget' but the previous stage did not end in budget" % where)
        if reason == "after-timeout" and "timeout" not in prev_states:
            E.append("%s: reason 'after-timeout' but the previous stage did not end in timeout" % where)

    # --- computations
    any_timeout_state = False
    separate_needed = a["observe"]["taken_on"] == "separate-run"
    for c in a["computations"]:
        cw = "%s computation %s" % (where, c["id"])
        es = c["execution_state"]
        states = set(es["states"])
        if es["determined"] and not states:
            E.append("%s: determined, but no state given" % cw)
        if "finished" in states and len(states) > 1:
            E.append("%s: 'finished' excludes every other state" % cw)
        if len(states & TERMINAL) > 1:
            E.append("%s: at most one of budget, timeout, error" % cw)
        if states & TERMINAL and states & {"finished"}:
            E.append("%s: 'finished' with %r" % (cw, sorted(states & TERMINAL)))
        if "error" in states and es["error_verbatim"] is None:
            E.append("%s: state error needs error_verbatim" % cw)
        if "timeout" in states:
            any_timeout_state = True
        steps = c["steps"]
        if steps.get("budget_enforced") is False and steps["budget_exhausted"]:
            E.append("%s: budget_exhausted, but the budget was not enforced" % cw)
        if ("budget" in states) != steps["budget_exhausted"]:
            E.append("%s: state budget and steps.budget_exhausted disagree" % cw)
        if steps["unit"] != lim["step_unit"]:
            E.append("%s: steps.unit %r, run.limits.step_unit is %r" % (cw, steps["unit"], lim["step_unit"]))
        if how == "reposed":
            enforced = steps.get("budget_enforced") is not False
            if steps["restart_cost"] is None:
                if enforced:
                    E.append("%s: reposed, but no measured restart cost (PROTOCOL.md, Running: measured restart cost plus the budget)" % cw)
            else:
                if steps["budget"] != lim["budget_steps"] + steps["restart_cost"]:
                    E.append("%s: a reposed stage's budget is restart cost + %d" % (cw, lim["budget_steps"]))
                if steps.get("restart_cost_method") not in ("in-run", "separate-run"):
                    E.append("%s: restart_cost without restart_cost_method" % cw)
        elif steps["budget"] != lim["budget_steps"]:
            E.append("%s: budget %r, expected %r" % (cw, steps["budget"], lim["budget_steps"]))
        for q in c["queries"]:
            qw = "%s query %s" % (cw, q["id"])
            ans = q["answers"]
            if len(ans) > q["cap"]:
                E.append("%s: %d answers over cap %d" % (qw, len(ans), q["cap"]))
            if [x["index"] for x in ans] != list(range(1, len(ans) + 1)):
                E.append("%s: answers are not indexed 1..%d" % (qw, len(ans)))
            if q["ended_by"] == "cap" and len(ans) != q["cap"]:
                E.append("%s: ended_by cap with %d answers, cap %d" % (qw, len(ans), q["cap"]))
            if q["ended_by"] in TERMINAL and q["ended_by"] not in states:
                E.append("%s: ended_by %s, but the computation's state lacks it" % (qw, q["ended_by"]))
            if q["collected_on"] == "separate-run":
                separate_needed = True
        for name, peak in (("alternatives", c["alternatives"]["peak"]), ("suspended", c["suspended"]["peak"])):
            if peak and peak["kind"] == "sampled" and mode != "storage":
                E.append("%s: a sampled %s maximum in a %s run (PROTOCOL.md, Modes of running)" % (cw, name, mode))
    if any_timeout_state and not a["safety_limit"]["hit"]:
        E.append("%s: state timeout, but safety_limit.hit is false" % where)
    if a["safety_limit"]["hit"] and not any_timeout_state:
        E.append("%s: safety limit hit, but no computation has state timeout" % where)

    for name, q in a["store"]["quantities"].items():
        pk = q["peak"]
        if pk and pk["kind"] == "sampled" and mode != "storage":
            E.append("%s: store %s is a sampled maximum in a %s run" % (where, name, mode))

    sr = a.get("separate_run")
    if separate_needed and sr is None:
        E.append("%s: answers or observation taken on a separate run, but separate_run is null" % where)
    if sr is not None:
        if not separate_needed:
            E.append("%s: separate_run given, but nothing is taken on it" % where)
        if sr["replayed"] != list(range(1, k + 1)):
            E.append("%s: the separate run replays stages 1..%d, got %r" % (where, k, sr["replayed"]))

    # --- effects
    for e in a["effects"]:
        if e["stage"] != k or e["attempt"] != n:
            E.append("%s: effect entry %d is marked stage %d attempt %d" % (where, e["seq"], e["stage"], e["attempt"]))
        if e["run_id"] != run["run_id"]:
            E.append("%s: effect entry %d has another run_id" % (where, e["seq"]))
        if mode != "behaviour" and e["log"] != "observation":
            E.append("%s: a %s run writes only to the observation log" % (where, mode))
        if e["during_replay_of"] is not None and (how != "reposed" or e["during_replay_of"] >= k):
            if not (sr is not None and e["log"] == "observation"):
                E.append("%s: effect entry %d during replay of stage %r, but the stage replays %r" % (where, e["seq"], e["during_replay_of"], replayed))
    if rec["effects"] is None and a["effects"]:
        E.append("%s: effect entries, but record.effects is null" % where)


def check_effects_log(rec, E):
    eff = rec["effects"]
    if eff is None:
        return
    log = eff["log_after_run"]
    if [e["seq"] for e in log] != list(range(1, len(log) + 1)):
        E.append("effects.log_after_run is not numbered 1..%d" % len(log))
    if any(e["log"] != "classification" for e in log):
        E.append("effects.log_after_run holds only the classification log")
    if eff["entries_before_run"] > len(log):
        E.append("effects.entries_before_run exceeds the log's length: the log is never reset")
    mine = [e for st in rec["stages"] for a in st["attempts"] for e in a["effects"] if e["log"] == "classification"]
    tail = log[eff["entries_before_run"]:]
    if json.dumps(mine, sort_keys=True) != json.dumps(tail, sort_keys=True):
        E.append("the classification entries of the attempts are not exactly the log's entries after entries_before_run")


# ------------------------------------------------------------------ main ---

def main(argv):
    args = argv[1:]
    schema_path, stages_path = DEFAULT_SCHEMA, DEFAULT_STAGES
    check_stages_only = False
    files = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--schema" and i + 1 < len(args):
            schema_path = args[i + 1]
            i += 2
        elif a == "--stages" and i + 1 < len(args):
            stages_path = args[i + 1]
            i += 2
        elif a == "--check-stages":
            check_stages_only = True
            i += 1
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            files.append(a)
            i += 1

    if check_stages_only:
        paths = files or [stages_path]
        bad = 0
        for p in paths:
            try:
                doc = load_json(p)
            except (OSError, ValueError) as e:
                print("%s: INVALID: cannot read: %s" % (p, e))
                bad += 1
                continue
            errs = check_stages_doc(doc)
            n_inst = sum(len(s.get("instances", [])) for pr in doc.get("problems", []) for s in pr.get("subproblems", []))
            n_sub = sum(len(pr.get("subproblems", [])) for pr in doc.get("problems", []))
            if errs:
                bad += 1
                print("%s: INVALID" % p)
                for e in errs:
                    print("  error: " + e)
            else:
                print("%s: valid (%d problems, %d sub-problems, %d instances)" % (p, len(doc.get("problems", [])), n_sub, n_inst))
        return 1 if bad else 0

    if not files:
        print(__doc__)
        return 2
    try:
        schema = Schema(load_json(schema_path))
        stages_doc = load_json(stages_path)
    except (OSError, ValueError) as e:
        print("cannot read schema or stages file: %s" % e)
        return 2

    bad = 0
    for p in files:
        try:
            rec = load_json(p)
        except (OSError, ValueError) as e:
            print("%s: INVALID: not readable JSON: %s" % (p, e))
            bad += 1
            continue
        errs = schema.errors(rec, schema.root)
        warns = []
        if not errs:
            try:
                errs, warns = check_record(rec, stages_doc, p)
                check_effects_log(rec, errs)
            except (KeyError, TypeError, IndexError) as e:
                errs = ["rule check failed on a malformed record: %r" % (e,)]
        if errs:
            bad += 1
            print("%s: INVALID" % p)
            for e in errs:
                print("  error: " + e)
        else:
            print("%s: valid" % p)
        for w in warns:
            print("  warning: " + w)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
