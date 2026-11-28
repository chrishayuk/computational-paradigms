#!/usr/bin/env python3
"""Write results/<system>/<configuration>/<problem>.md for a batch.

    tools/write-results.py SYSTEM PROBLEM... [--classes classes-1B]

Assembles, as PROTOCOL.md "Recording a result" lists, from what is already
committed: the raw records (results/SYSTEM/CONFIG/PROBLEM/raw/), both
classifiers' files (results/SYSTEM/classes/{A,B}/SYSTEM.json) and the token
files. It judges nothing: every class shown is a classifier's, every
figure a record's, and a figure a record does not have is shown as
unavailable (AMENDMENTS.md 3.1). Where the classifiers differ, both are
shown and the stage is marked disputed.
"""
import collections, glob, gzip, importlib.util, json, os, subprocess, sys

_spec = importlib.util.spec_from_file_location("outcome_agreement", os.path.join(os.path.dirname(os.path.abspath(__file__)), "outcome-agreement.py"))
OA = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(OA)   # one comparison for the result files and the agreement output

EVIDENCE = {
    ("absys", "absys"): "reconstructed", ("absys", "absys-depth-first"): "reconstructed",
    ("absys", "absys-wake-back"): "reconstructed",
    ("swi-prolog", "plain"): "modern", ("swi-prolog", "tabling"): "modern, with external mechanisms",
    ("swi-prolog", "coroutines"): "modern, with external mechanisms",
    ("swi-prolog", "constraints"): "modern, with external mechanisms", ("swi-prolog", "session"): "modern, extended",
    ("python", "core"): "modern", ("python", "stdlib-concurrency"): "modern, with external mechanisms",
    ("python", "extended"): "modern, extended",
    ("algol-60", "report"): "reconstructed", ("algol-60", "x1"): "reconstructed",
    ("algol-60", "x1sim"): "rehosted (compiler), reconstructed (run-time)",
}
S_LISTED = {
    ("swi-prolog", "session"): "`harnesses/swi-prolog/S/session-wait.pl` (158 tokens), loaded by the configuration",
    ("python", "extended"): "`S/search.py` (176 tokens), `S/suspend.py` (537), `S/propagate.py` (1,260): `harnesses/python/S-mechanisms.md`",
}
U = "unavailable"


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()


def fmt(v):
    if v is None or v == "" or v == []:
        return "—"
    if isinstance(v, list):
        return ", ".join(map(str, v))
    return str(v)


def j(v):
    return json.loads(v) if isinstance(v, str) and v[:1] in "{[" else v


def texts(system):
    """path of every program -> the path it is classed under."""
    m = {}
    lines = []
    for name in ("TEXTS.tsv", "TEXTS-1B.tsv", "TEXTS-1C.tsv"):   # the distinct texts of batches 1A, 1B and 1C
        if os.path.exists(f"results/{system}/tokens/{name}"):
            lines += list(open(f"results/{system}/tokens/{name}"))[1:]
    for line in lines:
        first, rest = (line.rstrip("\n").split("\t") + [""])[:2]
        m[first] = first
        for p in rest.split():
            m[p] = first
    return m


def tokens(system, path):
    return [l.rstrip("\n").split("\t") for l in open(f"results/{system}/tokens/{path}.tokens.tsv", encoding="utf-8")][1:]


def classes_of(spans, n):
    c = [None] * n
    for s in spans:
        for i in range(s["from"], s["to"] + 1):
            if 0 <= i < n:
                c[i] = s
    return c


def records(system, cfg, prob, mode, folder="raw"):
    """(instance, program path within the configuration) -> (file, record). The
    program path keeps a variants/ folder, as the classifiers name it."""
    out = {}
    fs = glob.glob(f"results/{system}/{cfg}/{prob}/{folder}/*.{mode}.*.json")
    fs += glob.glob(f"results/{system}/{cfg}/{prob}/{folder}/*.{mode}.*.json.gz")   # records over 50 MB
    for f in sorted(fs):
        d = json.load(gzip.open(f) if f.endswith(".gz") else open(f))
        prog = d["run"]["program"]["path"].split(f"programs/{system}/{cfg}/", 1)[-1]
        out[(d["run"]["instance"], prog)] = (f, d)
    return out


def stage_metrics(rec, stage):
    if rec is None:
        return {}
    f, d = rec
    st = [s for s in d["stages"] if s["stage"] == stage]
    if not st:
        return {}
    a = st[0]["attempts"][-1]
    c = (a.get("computations") or [{}])[0]
    steps = j(c.get("steps")) or {}
    alt = j(c.get("alternatives")) or {}
    sus = j(c.get("suspended")) or {}
    store = {k: v for k, v in ((a.get("store") or {}).get("quantities") or {}).items()}
    return {"steps": steps, "alt": alt, "sus": sus, "store": store, "attempts": len(st[0]["attempts"]),
            "safety": a.get("safety_limit", {}), "faults": d.get("harness_faults")}


def main(system, problems, classes="classes"):
    head = git("rev-parse", "--short", "HEAD")
    tmap = texts(system)
    cls = {w: json.load(open(f"results/{system}/{classes}/{w}/{system}.json")) for w in "AB"}
    for cfg in sorted(os.listdir(f"programs/{system}")):
        if not os.path.isdir(f"programs/{system}/{cfg}"):
            continue

        for prob in problems:
            prog_commit = git("log", "-1", "--format=%h", "--", f"programs/{system}/{cfg}/{prob}*",
                              f"programs/{system}/{cfg}/variants/{prob}*")   # this problem's programs
            beh = records(system, cfg, prob, "behaviour")
            if not beh:
                continue
            cost, stor = records(system, cfg, prob, "cost"), records(system, cfg, prob, "storage")
            anyrec = next(iter(beh.values()))[1]["run"]
            L = []
            w = L.append
            w(f"# {system} / {cfg} / {prob}\n")
            w("*Assembled by `tools/write-results.py` from the raw records and both classifiers' files; "
              "it judges nothing. Where the classifiers differ, both are given.*\n")
            w("| | |\n|---|---|")
            w(f"| specification | `spec-1.0.1` (records carry the harness's `spec_tag`: `{anyrec.get('spec_tag')}`) |")
            sysv = anyrec.get("system_version") or anyrec.get("system") or {}
            w(f"| system | see each record's `run` (commits of the pinned image); first record: `{next(iter(beh.values()))[0]}` |")
            w(f"| configuration | {cfg} |")
            w(f"| evidence class | {EVIDENCE.get((system, cfg), U)} (`systems/{system}/README.md`) |")
            w(f"| programs | `programs/{system}/{cfg}/` at `{prog_commit}`, unchanged since; author's notes `programs/{system}/README.md` |")
            w(f"| precursor seen | no (the author's statement, `programs/{system}/README.md`; audit `programs/AUDIT-1A.md`) |")
            w(f"| S mechanisms listed at phase 4 | {S_LISTED.get((system, cfg), 'none')} |")
            w(f"| hidden variants | not yet run: wave-1b is opened and run by the verifier after every primary result of wave 1 is committed (`AMENDMENTS.md` 1) |")
            w(f"| classifiers | A: Claude agent; B: Codex (codex-cli 0.166.0); brief `sandbox/briefs/classifier.md`; files `results/{system}/{classes}/` |")
            inval = sorted(os.path.basename(f) for f, _ in beh.values() if f.endswith(".INVALID.json"))
            if inval:
                w(f"| harness faults | behaviour records the harness kept as invalid (step accounting): {', '.join('`' + x + '`' for x in inval)}; classified from them, flagged |")
            w("")

            # ---- outcomes
            w("## Stages\n")
            w("Semantic / representation / simplification / execution state, per classifier. "
              "*id.* = residual identical to the posed information. Steps from the cost run, each field as the harness records it "
              "(`stage`, `to_end`, `restated`, `restart_cost`; harnesses/README.md).\n")
            w("| instance | program | stage | A | B | agree | steps: stage | to end | restated | restart cost | alternatives | suspended |")
            w("|---|---|---|---|---|---|---|---|---|---|---|---|")
            outc = {wch: collections.defaultdict(list) for wch in "AB"}
            for wch in "AB":
                for e in cls[wch]["outcomes"]:
                    if e["configuration"] == cfg and e.get("final_attempt") is not False:
                        prog = e["program"][len(cfg) + 1:] if e["program"].startswith(cfg + "/") else e["program"]
                        outc[wch][(e["instance"], prog, e["stage"])].append(e)
            keys = sorted({k for wch in "AB" for k in outc[wch] if (k[0], k[1]) in beh}, key=lambda k: (k[0], k[1], k[2]))
            obs = []
            for k in keys:
                def expand(es):
                    out = []
                    for e in es:
                        if e.get("reached") is False:
                            out.append(("", "not reached")); continue
                        sems = [(e.get("reading"), e.get("semantic"))]
                        if isinstance(e.get("semantic"), str) and "reading)" in e["semantic"]:
                            sems = [(x.split("(")[1].split()[0], x.split("(")[0].strip()) for x in e["semantic"].split(";")]
                        for rd, sem in sems:
                            idp = " *id.*" if e.get("identical_to_posed") is True and e.get("representation") == "residual" else ""
                            body = " / ".join(fmt(v) for v in (sem, e.get("representation"), e.get("simplification"), e.get("execution_state"))) + idp
                            out.append((rd or "", body))
                    return sorted(set(out))
                ea, eb = expand(outc["A"].get(k, [])), expand(outc["B"].get(k, []))
                show = lambda es: "; ".join((f"{rd}: " if rd else "") + b for rd, b in es)
                a, b = show(ea), show(eb)
                ag = "yes" if not OA.compare(outc["A"].get(k, []), outc["B"].get(k, [])) else \
                    "**disputed** (" + ", ".join(x[0] for x in OA.compare(outc["A"].get(k, []), outc["B"].get(k, []))) + ")"
                m = stage_metrics(cost.get((k[0], k[1])), k[2])
                st = m.get("steps", {})
                mv = lambda d, x: U if not d or d.get(x) is None else d.get(x)
                w(f"| {k[0]} | `{k[1]}` | {k[2]} | {a} | {b} | {ag} | {mv(st, 'stage')} | {mv(st, 'to_end')} | {mv(st, 'restated')} | "
                  f"{mv(st, 'restart_cost')} | {mv(m.get('alt'), 'at_boundary')} | {mv(m.get('sus'), 'at_boundary')} |")
                for wch in "AB":
                    for e in outc[wch].get(k, []):
                        if e.get("observations") or e.get("residual_equivalence"):
                            obs.append((k, wch, e.get("observations"), e.get("residual_equivalence"), e.get("rule")))
            w("")

            # ---- storage
            w("## Store at the stage boundary and peak (storage run)\n")
            rows = []
            for (inst, prog), rec in stor.items():
                for s in rec[1]["stages"]:
                    q = stage_metrics(rec, s["stage"]).get("store", {})
                    cells = "; ".join(f"{n}: {fmt(v.get('boundary')) if v.get('boundary') is not None else U} / "
                                      f"{fmt((v.get('peak') or {}).get('value')) if v.get('peak') else U} {v.get('unit', '')}"
                                      for n, v in q.items()) or U
                    rows.append(f"| {inst} | `{prog}` | {s['stage']} | {cells} |")
            if rows:
                w("| instance | program | stage | quantity: boundary / peak unit |\n|---|---|---|---|")
                L.extend(rows)
            else:
                w(f"No storage run in this configuration.")
            w("")

            # ---- tokens
            w("## Tokens by class, per classifier\n")
            w("| program | tokens | A: P C R S H | B: P C R S H | agreed | disputed (A→B: count, constructs) |")
            w("|---|---|---|---|---|---|")
            progs = sorted({p for (_, p) in beh})
            for p in progs:
                path = tmap.get(f"{cfg}/{p}")
                if path is None:
                    w(f"| `{p}` | {U} | | | | |"); continue
                key = f"{cfg}/{p}" if f"{cfg}/{p}" in cls["A"]["tokens"] or f"{cfg}/{p}" in cls["B"]["tokens"] else path
                toks = tokens(system, path)
                n = len(toks)
                ca = classes_of(cls["A"]["tokens"].get(key, cls["A"]["tokens"].get(path, [])), n)
                cb = classes_of(cls["B"]["tokens"].get(key, cls["B"]["tokens"].get(path, [])), n)
                tot = lambda c: " ".join(str(sum(1 for s in c if s and s["class"] == x)) for x in "PCRSH")
                dis = collections.Counter()
                cons = collections.defaultdict(set)
                for sa, sb in zip(ca, cb):
                    if sa and sb and sa["class"] != sb["class"]:
                        dis[(sa["class"], sb["class"])] += 1
                        cons[(sa["class"], sb["class"])].add(f"{sa.get('construct', '')} / {sb.get('construct', '')}"[:80])
                agreed = n - sum(dis.values())
                d = "; ".join(f"{x}→{y}: {c} ({' · '.join(sorted(cons[(x, y)])[:3])}{' …' if len(cons[(x, y)]) > 3 else ''})"
                              for (x, y), c in dis.most_common()) or "—"
                shared = "" if path == f"{cfg}/{p}" else f" (text of `{path}`)"
                w(f"| `{p}`{shared} | {n} | {tot(ca)} | {tot(cb)} | {agreed}/{n} | {d} |")
            w("")

            # ---- expressibility
            w("## Expressibility\n")
            w("| sub-problem | direction | A | B |\n|---|---|---|---|")
            ex = collections.defaultdict(dict)
            for wch in "AB":
                for e in cls[wch]["expressibility"]:
                    if e["configuration"] == cfg and e["subproblem"].startswith(prob):
                        ex[(e["subproblem"], fmt(e.get("direction")))][wch] = f"{e['expressibility']}: {e.get('reason', '')}"
            for (sp, dr), v in sorted(ex.items()):
                w(f"| {sp} | {dr} | {v.get('A', U)} | {v.get('B', U)} |")
            w(f"\nThe author's own reading is in `programs/{system}/README.md`.\n")

            # ---- mode differences
            md = [(wch, e) for wch in "AB" for e in cls[wch].get("mode_differences", [])
                  if e.get("configuration") == cfg and str(e.get("instance", "")).startswith(prob)]
            w("## Cost and storage runs that differ from behaviour\n")
            if md:
                for wch, e in md:
                    w(f"- **{wch}**, {e.get('instance')} `{e.get('program')}` {e.get('mode')} stage {e.get('stage')}: {e.get('note') or json.dumps(e.get('this_mode'))[:400]}")
            else:
                w("None, by either classifier.")
            w("")

            # ---- measurement reruns
            rr = {**records(system, cfg, prob, "cost", "raw-rerun-m2"), **{k + ("storage",): v for k, v in records(system, cfg, prob, "storage", "raw-rerun-m2").items()}}
            if rr:
                w("## Labelled measurement reruns (`raw-rerun-m2/`)\n")
                w("Reruns of cost or storage runs that reached the safety limit, with the fixed measurement build (`results/absys/RERUN-M2.md`). The original records stand.\n")
                w("| instance | program | mode | stage | attempts | state | steps: stage | derivations: boundary / peak |\n|---|---|---|---|---|---|---|---|")
                for key, (f, d) in sorted(rr.items(), key=str):
                    for s_ in d["stages"]:
                        a = s_["attempts"][-1]; c = (a.get("computations") or [{}])[0]
                        stp = j(c.get("steps")) or {}; es = j(c.get("execution_state")) or {}
                        der = ((a.get("store") or {}).get("quantities") or {}).get("derivations") or {}
                        pk = der.get("peak") or {}
                        w(f"| {key[0]} | `{key[1]}` | {d['run']['mode']} | {s_['stage']} | {len(s_['attempts'])} | {fmt(es.get('states'))} | {fmt(stp.get('stage')) if stp.get('stage') is not None else U} | {der.get('boundary', U) if der.get('boundary') is not None else U} / {pk.get('value', U) if pk else U}{' (' + pk['kind'] + ')' if pk.get('kind') else ''} |")
                w("")

            # ---- late definition
            ld = [(wch, e) for wch in "AB" for e in cls[wch].get("late_definition", []) if e.get("configuration") == cfg
                  and os.path.basename(e.get("program", "")).startswith(prob)]
            if ld:
                w("## Late definition: what an application waits for before its definition arrives\n")
                w("| program | A | B |\n|---|---|---|")
                byp = collections.defaultdict(dict)
                for wch, e in ld:
                    byp[e["program"].split(cfg + "/", 1)[-1]][wch] = e
                for prog, v in sorted(byp.items()):
                    w(f"| `{prog}` | **{v.get('A', {}).get('kind', U)}**: {v.get('A', {}).get('evidence', '')} | **{v.get('B', {}).get('kind', U)}**: {v.get('B', {}).get('evidence', '')} |")
                w("")

            # ---- supporting mechanisms
            sm = [(wch, e) for wch in "AB" for e in cls[wch].get("s_mechanisms", []) if e.get("configuration") == cfg
                  and os.path.basename(e.get("program", "")).startswith(prob) and e.get("mechanism")]
            if sm:
                w("## Supporting mechanisms used, per classifier\n")
                w("| program | classifier | mechanism | listed at phase 4 | tokens |\n|---|---|---|---|---|")
                for wch, e in sorted(sm, key=lambda x: (x[1].get("program", ""), x[0], str(x[1].get("mechanism")))):
                    w(f"| `{e['program'].split(cfg + '/', 1)[-1]}` | {wch} | {e.get('mechanism')} | {fmt(e.get('listed_at_phase_4'))} | {fmt(e.get('tokens'))} |")
                w("")

            # ---- observations
            w("## Observations and residual equivalence, per classifier\n")
            for k, wch, o, r, rule in obs:
                w(f"- {k[0]} `{k[1]}` stage {k[2]}, **{wch}**: {fmt(o)}"
                  + (f" *Equivalence:* {r}" if r else "") + (f" *Rule:* {rule}" if rule else ""))
            w("")
            os.makedirs(f"results/{system}/{cfg}", exist_ok=True)
            open(f"results/{system}/{cfg}/{prob}.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
            print(f"results/{system}/{cfg}/{prob}.md")


if __name__ == "__main__":
    a = sys.argv[1:]
    classes = "classes"
    if "--classes" in a:
        i = a.index("--classes"); classes = a[i + 1]; del a[i:i + 2]
    main(a[0], a[1:], classes)
