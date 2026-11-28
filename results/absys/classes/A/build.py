# Builds absys.json: token classes, outcomes, mode differences, expressibility.
# Classifier A. Reads only the permitted files; runs nothing of the system.
import json, glob, os, re, collections
REPO = '.'
RES = f'{REPO}/results/absys'
OUT = 'results/absys/classes/A/absys.json'
CONFIGS = ['absys', 'absys-depth-first', 'absys-wake-back']

# ---------------------------------------------------------------- tokens
def load_tokens(path):
    rows = [l.rstrip('\n').split('\t') for l in open(path, encoding='utf-8')][1:]
    return [(int(i), int(ln), t) for i, ln, t in rows]

R_CONST = "rule 1 (removing the constants-block line changes what the stage asserts); harness README 3.12: the block is classed by METRICS.md's rules, not H"
R_INFO = "rule 1; P covers 'the information of each stage' and the equality connective"
R_ARITH = "rule 8 and SPECIFICATION Arithmetic: a primitive arithmetic relation written as the relation, served in every direction by the core"
R_DEF = "rule 3 (transcription of the problem's definition by cases, in presentation order); rule 10 for the tokens that introduce and close it"
R_OR = "rule 6 (a disjunction the problem states: the definition's two cases); rule 20 would give the same class"
R_QUERY = "rule 1; P covers the query"

def spans_for(tokens):
    """Spans by construct. tokens: list of (index, line, text)."""
    spans = []
    i = 0; n = len(tokens)
    def add(a, b, cls, construct, rule):
        spans.append({"from": tokens[a][0], "to": tokens[b][0], "class": cls, "construct": construct, "rule": rule})
    # group by line for top-level constructs, with finer splitting inside lambdas
    lines = collections.OrderedDict()
    for k, (ix, ln, t) in enumerate(tokens):
        lines.setdefault(ln, []).append(k)
    lnums = list(lines)
    li = 0
    while li < len(lnums):
        ks = lines[lnums[li]]
        texts = [tokens[k][2] for k in ks]
        first = texts[0]
        if len(texts) >= 3 and texts[1] == '=' and texts[2] == 'lambda':
            # procedure definition: header line, then 'begin {' case1 'or' / case2 '} end'
            name = first.rstrip("'")
            l2 = lines[lnums[li + 1]]; l3 = lines[lnums[li + 2]]
            t2 = [tokens[k][2] for k in l2]; t3 = [tokens[k][2] for k in l3]
            assert t2[0] == 'begin' and t2[1] == '{' and t2[-1] == 'or', t2
            assert t3[-2:] == ['}', 'end'], t3
            add(ks[0], l2[1], 'P', f"{name}: definition head '{name}' = lambda with its parameters, and the opening 'begin {{' of its body (definition of {name} by cases)", R_DEF)
            add(l2[2], l2[-2], 'P', f"{name} case 1: " + ' '.join(t2[2:-1]) + (" (conc(<>, b, b))" if name == 'conc' else " (rev(<>, <>))"), R_DEF)
            add(l2[-1], l2[-1], 'P', f"'or' between {name}'s cases 1 and 2", R_OR)
            # case 2: split into the head equation(s) and the body goals
            body = l3[:-2]
            parts = []; cur = []; depth = 0
            for k in body:
                t = tokens[k][2]
                cur.append(k)
                if t in '[(': depth += 1
                if t in '])':
                    depth -= 1
                    if depth == 0:
                        parts.append(cur); cur = []
            assert not cur, cur
            for p in parts:
                txt = ' '.join(tokens[k][2] for k in p)
                if p[0] != body[0] and tokens[p[0]][2] in ('conc', 'rev'):
                    what = f"{name} case 2 body conjunct (in the problem's order): {txt}"
                else:
                    what = f"{name} case 2 head equation: {txt}"
                add(p[0], p[-1], 'P', what, R_DEF)
            add(l3[-2], l3[-1], 'P', f"closing '}} end' of {name}'s body", R_DEF)
            li += 3; continue
        if first == 'begin':
            # P02c: begin R1 R2 R3 end
            assert texts[-1] == 'end'
            add(ks[0], ks[0], 'P', "'begin' opening the stage's conjunction of R1, R2, R3 (Absys 1's conjunction bracket)", "rule 10 with the P list's conjunction connective; see notes (could be argued C under rule 1)")
            inner = ks[1:-1]
            # split at each '=' followed by one operand: relations are 'a op b = c'
            grp = []; rel = []
            for k in inner:
                rel.append(k)
                if len(rel) >= 2 and tokens[rel[-2]][2] == '=':
                    grp.append(rel); rel = []
            assert not rel and len(grp) == 3, grp
            for g, lab in zip(grp, ['R1', 'R2', 'R3']):
                add(g[0], g[-1], 'P', f"{lab}: " + ' '.join(tokens[k][2] for k in g), R_ARITH)
            add(ks[-1], ks[-1], 'P', "'end' closing the stage's conjunction", "rule 10 with the P list's conjunction connective")
            li += 1; continue
        txt = ' '.join(texts)
        yield_line = lnums[li]
        if texts[1] == '=' and not any(t in ('conc', 'rev') for t in texts):
            # constants-block entries are on lines inside the block; detect by name lookup later
            spans.append({"from": tokens[ks[0]][0], "to": tokens[ks[-1]][0], "class": "P", "construct": txt, "rule": None, "_line": yield_line})
        else:
            add(ks[0], ks[-1], 'P', f"stage information / query: {txt}", R_QUERY)
        li += 1
    return spans

def classify_text(cfg, fname):
    tokpath = f'{RES}/tokens/{cfg}/{fname}.tokens.tsv'
    prog = open(f'{REPO}/programs/absys/{cfg}/{fname}', encoding='utf-8').read().splitlines()
    # constants block lines
    b = next(i for i, l in enumerate(prog) if 'CONSTANTS BEGIN' in l) + 1
    e = next(i for i, l in enumerate(prog) if 'CONSTANTS END' in l) + 1
    toks = load_tokens(tokpath)
    spans = spans_for(toks)
    for s in spans:
        ln = s.pop('_line', None)
        if ln is None: continue
        if b < ln < e:
            cm = re.search(r'%\s*(.*)$', prog[ln - 1])
            s['construct'] = f"constants block entry: {s['construct']} (the {cm.group(1) if cm else 'stage'} constant)"
            s['rule'] = R_CONST
        else:
            s['construct'] = f"stage information: {s['construct']}"
            s['rule'] = R_INFO
    # coverage check
    idx = [t[0] for t in toks]
    cov = []
    for s in spans: cov.extend(range(s['from'], s['to'] + 1))
    assert sorted(cov) == idx and len(cov) == len(set(cov)), fname
    return spans, len(toks)

texts = [l.rstrip('\n').split('\t') for l in open(f'{RES}/tokens/TEXTS.tsv')][1:]
tokens_out = {}; totals = collections.Counter(); per_text = {}
for first, others in texts:
    cfg, fname = first.split('/')
    spans, n = classify_text(cfg, fname)
    tokens_out[first] = spans
    per_text[first] = n
    for s in spans: totals[s['class']] += s['to'] - s['from'] + 1
    # check that the other configurations' token files are byte-identical (same text, same classes)
    for o in others.split():
        oc, of = o.split('/')
        assert open(f'{RES}/tokens/{oc}/{of}.tokens.tsv', 'rb').read() == open(f'{RES}/tokens/{cfg}/{fname}.tokens.tsv', 'rb').read()
        assert open(f'{REPO}/programs/absys/{oc}/{of}', 'rb').read() == open(f'{REPO}/programs/absys/{cfg}/{fname}', 'rb').read()

# ---------------------------------------------------------------- outcomes
def rec(cfg, inst, mode):
    g = glob.glob(f'{RES}/{cfg}/{inst[:3]}/raw/{inst}.{mode}.*.json')
    assert len(g) == 1, (cfg, inst, mode, g)
    return g[0]

# P02b orders: which relations have arrived after stage k
def p02_judgement(rels, cfg_rec_stage):
    rels = frozenset(rels)
    J = {
      frozenset(['R1']): dict(semantic='complete', representation='residual', simplification='reduced', identical_to_posed=True,
            residual_size='held: u + v = 16 (1 relation, 2 occurrences of unknowns); input: R1 (1 relation, 2 occurrences)',
            residual_equivalence="equivalent: the held relation is R1 itself, and w does not occur (free), which is the valid outcome 'u + v = 16, w free'. No smaller representation: the solution set is infinite, so no explicit form, and one relation cannot lose an occurrence (SPECIFICATION's own example, P02 stage 1)."),
      frozenset(['R2']): dict(semantic='complete', representation='residual', simplification='reduced', identical_to_posed=True,
            residual_size='held: w * u = v (1 relation, 3 occurrences); input: R2 (1 relation, 3 occurrences)',
            residual_equivalence="equivalent: the held relation is R2 itself, the valid outcome 'v = w * u (infinite)'. Infinite solution set; one primitive relation over three unknowns cannot be smaller."),
      frozenset(['R3']): dict(semantic='complete', representation='solved form', simplification=None, identical_to_posed=None, residual_size=None,
            residual_equivalence="solved form u = 2 with v and w not occurring (free): equals the valid outcome 'u = 2; v and w free'."),
      frozenset(['R1', 'R2']): dict(semantic='complete', representation='residual', simplification='reducible', identical_to_posed=True,
            residual_size='held: u + v = 16 and w * u = v (2 relations, 5 occurrences); input: R1 and R2 (2 relations, 5 occurrences)',
            residual_equivalence="equivalent, by script (p02_check.py): over the integers, u + v = 16 and w*u = v give u*(w+1) = 16, so u divides 16; enumerating every divisor u of 16 and solving gives exactly the ten triples of the problem file, and every one of the ten satisfies both held relations. Reducible: the ten explicit triples have no relation left to decide, so a smaller representation exists by SPECIFICATION's measure (as in its P07b example), which the system did not reach."),
      frozenset(['R1', 'R3']): dict(semantic='complete', representation='solved form', simplification=None, identical_to_posed=None, residual_size=None,
            residual_equivalence="solved form u = 2, v = 14, w not occurring (free): equals the valid outcome 'u = 2, v = 14; w free'."),
      frozenset(['R2', 'R3']): dict(semantic='complete', representation='residual', simplification='reduced', identical_to_posed=False,
            residual_size='held: u = 2 and w * 2 = v (1 relation left, 2 occurrences); input: R2 and R3 (2 relations, 4 occurrences: w, u, v in w * u = v, and u in u + 10 = 12)',
            residual_equivalence="equivalent: u = 2 bound and w*2 = v held is the valid outcome 'u = 2, v = 2w, for every integer w'. Reduced: the solution set is infinite and one relation over two unknowns is the least that can express it. Not identical to the posed information: R3 was solved and its value substituted into R2."),
      frozenset(['R1', 'R2', 'R3']): dict(semantic='complete', representation='explicit', simplification=None, identical_to_posed=None, residual_size=None,
            residual_equivalence="explicit u = 2, v = 14, w = 7: the single valid triple."),
    }
    return dict(J[rels])

STATIC = {}  # (instance, stage) -> judgement dict
STATIC[('P01a', 1)] = dict(semantic='complete', representation='solved form', simplification=None, identical_to_posed=None, residual_size=None,
    residual_equivalence="x and y identified by a suspended equation x = y (the system's representation of two unknowns made equal); z does not occur (free). Equals 'every assignment with x = y; z free'.",
    obs_unknowns="x = y held as one suspended equation between the two unknowns (a recorded equation, not one shared variable); z does not occur")
STATIC[('P01a', 2)] = dict(semantic='complete', representation='solved form', simplification=None, identical_to_posed=None, residual_size=None,
    residual_equivalence="x, y, z identified through two suspended equations x = y, y = z: equals 'every assignment with x = y = z'.",
    obs_unknowns="x = y = z held as two suspended equations, x = y and y = z")
STATIC[('P01a', 3)] = dict(semantic='complete', representation='explicit', simplification=None, identical_to_posed=None, residual_size=None,
    residual_equivalence="x = y = z = 2, explicit: the valid outcome.",
    obs_unknowns="none remain unknown; the value 2 reached x, y and z (cost run: 6 steps in the stage, 3 reactivating events)")
STATIC[('P01b', 1)] = dict(semantic='complete', representation='solved form', simplification=None, identical_to_posed=None, residual_size=None,
    residual_equivalence="t = [1;2&m2] with s identified with m2 by a suspended equation: t = <1,2> ++ s, s free, which is the valid outcome. The program's conc does not test that s is a sequence (see notes), but the solved form t = <1,2> ++ s only denotes sequences s, as the valid outcome does.",
    obs_unknowns="s identified with an internal unknown m2 by a suspended equation s = m2; t bound to the open list [1;2&m2]; the conc application has been fully elaborated (derivation #5 is the only survivor of the or-branches)")
STATIC[('P01b', 2)] = dict(semantic='complete', representation='explicit', simplification=None, identical_to_posed=None, residual_size=None,
    residual_equivalence="s = [3], t = [1;2;3]: the valid outcome.",
    obs_unknowns="none remain unknown; the value of s reached t through the suspended equation s = m2 (cost run: 4 steps in the stage, 2 reactivating events)")
STATIC[('P03a', 1)] = dict(semantic='complete', representation='explicit', simplification=None, identical_to_posed=None, residual_size=None,
    residual_equivalence="c = [1;2;3], one derivation: the one valid outcome; answer completeness 1/1, 0 invalid.", obs_unknowns="none remain unknown")
STATIC[('P03b', 1)] = dict(semantic='complete', representation='explicit', simplification=None, identical_to_posed=None, residual_size=None,
    residual_equivalence="three derivations, (a, b) = ([], [1;2]), ([1], [2]), ([1;2], []): exactly the three valid outcomes, in that order; answer completeness 3/3, 0 invalid. The system reports it has every answer (no derivation still elaborating, none suspended).",
    obs_unknowns="none remain unknown in any derivation")
STATIC[('P03c', 1)] = dict(semantic='complete', representation='explicit', simplification=None, identical_to_posed=None, residual_size=None,
    residual_equivalence="b = [2;3]: the one valid outcome; 1/1, 0 invalid.", obs_unknowns="none remain unknown")
STATIC[('P03d', 1)] = dict(semantic='complete', representation='explicit', simplification=None, identical_to_posed=None, residual_size=None,
    residual_equivalence="a = [1;2]: the one valid outcome; 1/1, 0 invalid.", obs_unknowns="none remain unknown")
STATIC[('P03e', 1)] = dict(semantic='complete', representation='explicit', simplification=None, identical_to_posed=None, residual_size=None,
    residual_equivalence="b = [3;2;1]: the one valid outcome; 1/1, 0 invalid.", obs_unknowns="none remain unknown")
STATIC[('P02c', 1)] = dict(semantic='complete', representation='explicit', simplification=None, identical_to_posed=None, residual_size=None,
    residual_equivalence="u = 2, v = 14, w = 7: the valid outcome.", obs_unknowns="none remain unknown")

P02_UNK = {
  frozenset(['R1']): "u and v uninstantiated, held only by the suspended relation u + v = 16 (waits for two of its numbers); w does not occur",
  frozenset(['R2']): "w, u and v uninstantiated, held by the suspended relation w * u = v",
  frozenset(['R3']): "u = 2; v and w do not occur (free)",
  frozenset(['R1', 'R2']): "u, v, w uninstantiated, held by the two suspended relations u + v = 16 and w * u = v",
  frozenset(['R1', 'R3']): "u = 2, v = 14; w does not occur (free)",
  frozenset(['R2', 'R3']): "u = 2; w and v uninstantiated, held by the suspended relation w * 2 = v",
  frozenset(['R1', 'R2', 'R3']): "none remain unknown",
}

def p02_order(inst):
    if inst == 'P02a': return ['R1', 'R2', 'R3']
    return re.findall(r'R\d', inst.split('.')[1])

def facts(path):
    d = json.load(open(path))
    out = {}
    for s in d['stages']:
        out[s['stage']] = s['attempts']
    return d, out

outcomes = []
mode_diffs = []
cost_info = {}
for cfg in CONFIGS:
    for b in sorted(glob.glob(f'{RES}/{cfg}/P0?/raw/*.behaviour.*.json')):
        inst = os.path.basename(b).split('.behaviour')[0]
        d, st = facts(b)
        program = os.path.basename(d['run']['program']['path'])
        # cost run for steps
        dc, stc = facts(rec(cfg, inst, 'cost'))
        relpath = os.path.relpath(b, REPO)
        for k, atts in st.items():
            for a in atts:
                final = a is atts[-1]
                c = a['computations'][0]
                es = c['execution_state']['states']
                q = c['queries'][0]
                alts = c['alternatives']; su = c['suspended']
                ccomp = stc[k][-1]['computations'][0]['steps']
                steps_txt = (f"cost run: {ccomp['stage']} steps in the stage, {ccomp['restated']} restated, "
                             f"{(ccomp['repeated_work'] or {}).get('reactivating_events')} reactivating events" if ccomp['stage'] is not None
                             else "cost run: steps unavailable (the cost run's attempts both hit the safety limit)")
                base = dict(configuration=cfg, instance=inst, program=program, record=relpath, stage=k,
                            attempt=a['attempt'], final_attempt=final, reached=True)
                if inst.startswith('P02') and inst != 'P02c':
                    order = p02_order(inst); rels = order[:k]
                    J = p02_judgement(rels, None); unk = P02_UNK[frozenset(rels)]
                    J['obs_unknowns'] = unk
                elif inst == 'P01c':
                    J = None
                elif inst == 'P03f':
                    J = None
                else:
                    J = dict(STATIC[(inst, k)])
                susp_items = {kk: vv for kk, vv in (su['items'] or {}).items() if vv}
                obs_common = (f"alternatives held: {alts['at_boundary']} derivation(s), held as {alts['held_as']}"
                              + (" (all live at once)" if alts['held_as'] == 'all-live' else " (all held, only the first running one elaborated: depth-first)")
                              + f"; suspended work: {su['at_boundary']} process(es) the printer shows {susp_items if susp_items else ''}"
                              + f"; answers collected {len(q['answers'])}, ended_by {q['ended_by']}; {steps_txt}"
                              + "; no conclusion of an earlier stage withdrawn; no manual action")
                if inst == 'P01c':
                    for reading, sem in [('finite', 'unsound'), ('rational', 'complete')]:
                        o = dict(base, reading=reading, semantic=sem, representation='cyclic', simplification=None, identical_to_posed=None,
                                 residual_size=None, execution_state=es,
                                 residual_equivalence=("x = [1&↻], printed as a cyclic list, is the rational tree <1,1,1,...>: the one solution under the rational reading."
                                                       if reading == 'rational' else
                                                       "x = [1&↻] reports a (cyclic) solution where the finite reading has none, so the report denotes an outcome that is not valid (problem file: a cyclic value is unsound under the finite reading)."),
                                 observations=("unknown x bound to a cyclic term, printed with ↻ ('the enclosing list again'); configuration has no occur check (docs/decisions.md rule 8, cited in the program and the systems file); " + obs_common),
                                 rule="SPECIFICATION Outcomes 1-3; P01c: 'A cyclic value, presented as such, is complete under the rational reading and unsound under the finite one'")
                        outcomes.append(o)
                    continue
                if inst == 'P03f':
                    if 'timeout' in es:
                        o = dict(base, semantic='none reported', representation=None, simplification=None, identical_to_posed=None,
                                 residual_size=None, execution_state=es,
                                 residual_equivalence="nothing was collected before the safety limit (60 s) stopped the attempt",
                                 observations=f"attempt 1 of 2: SIGKILL at the 60 s safety limit, rerun once at 600 s (attempt 2, reposed as a safety rerun); {obs_common}",
                                 rule="SPECIFICATION Outcomes 3 (timeout; answers before the limit classified on the semantic axis: none); PROTOCOL Running, safety limit")
                        outcomes.append(o); continue
                    nder = alts['at_boundary']
                    o = dict(base, semantic='complete', representation='explicit', simplification=None, identical_to_posed=None,
                             residual_size=None, execution_state=es,
                             residual_equivalence=(f"one hibernating derivation with a = [3;2;1], the one valid outcome; the other {nder-1} derivations are still elaborating when the budget ran out. "
                                                   "Checked by script (p03f_check.py): every one of them already fixes a prefix of a of at least "
                                                   + ("32" if nder == 900 else "106") +
                                                   " elements, while every solution of rev(a, <1,2,3>) has 3, so each still-elaborating derivation denotes no solution (an inconsistency not yet detected). "
                                                   "So the report denotes exactly {a = <3,2,1>}: complete; answer completeness 1/1, 0 invalid answers. The problem file: 'a system that reports it and then runs out of budget is complete with budget'."),
                             observations=(f"representation classed on the valid explicit derivation; the other form, {nder-1} still-elaborating derivations each with an open or over-long a, suspended equations between element unknowns and pending rev/conc goals, is recorded here (it is a residual whose inconsistency is undetected). "
                                           f"The first of the {len(q['answers'])} answers collected (cap 20) is the valid one; the rest are unfinished derivations, not solutions. "
                                           "The system does not know it has every answer: it goes on to the budget (10^6 steps). "
                                           + ("Attempt 2 (safety rerun at 600 s) after attempt 1 timed out at 60 s. " if a['attempt'] == 2 else "")
                                           + obs_common),
                             rule="SPECIFICATION Outcomes 1-3; Representation, 'two forms': classed on the more explicit valid form; P03 Observations on P03f")
                    outcomes.append(o); continue
                obs_unk = J.pop('obs_unknowns')
                o = dict(base, **{kk: J[kk] for kk in ['semantic', 'representation', 'simplification', 'identical_to_posed', 'residual_size']},
                         execution_state=es, residual_equivalence=J['residual_equivalence'],
                         observations=f"unknowns: {obs_unk}; {obs_common}",
                         rule="SPECIFICATION Outcomes 1-3 and simplification; 'reported' = what observe() reads at the end of the stage")
                # note on store association
                if inst.startswith('P02') and es == ['finished']:
                    sc = facts(rec(cfg, inst, 'storage'))[1][k][-1]['store']['quantities'].get('susp_relations', {})
                    if sc.get('boundary'):
                        o['observations'] += (f"; the storage run's susp_relations is {sc['boundary']} at the boundary although the printer shows nothing suspended: "
                                              "relations stay associated with their variables after every one is bound (docs/decisions.md rule 10, harness README 4); execution state read as finished, as the harness did")
                outcomes.append(o)

# mode differences
for cfg in CONFIGS:
    for b in sorted(glob.glob(f'{RES}/{cfg}/P0?/raw/*.behaviour.*.json')):
        inst = os.path.basename(b).split('.behaviour')[0]
        _, sb = facts(b)
        for mode in ['cost', 'storage']:
            m = rec(cfg, inst, mode)
            _, sm = facts(m)
            for k in sb:
                ab = sb[k][-1]; am = sm[k][-1]
                cb = ab['computations'][0]; cm = am['computations'][0]
                same = (cb['execution_state']['states'] == cm['execution_state']['states'] and ab['print'] == am['print']
                        and [x['verbatim'] for x in cb['queries'][0]['answers']] == [x['verbatim'] for x in cm['queries'][0]['answers']])
                if same: continue
                bo = [o for o in outcomes if o['configuration'] == cfg and o['instance'] == inst and o['stage'] == k and o['final_attempt']][0]
                mode_diffs.append(dict(configuration=cfg, instance=inst, program=os.path.basename(b).split('.')[0] + '.ab1', mode=mode,
                    record=os.path.relpath(m, REPO), stage=k,
                    behaviour=dict(semantic=bo['semantic'], representation=bo['representation'], execution_state=bo['execution_state']),
                    this_mode=dict(semantic='none reported', representation=None, execution_state=[a['computations'][0]['execution_state']['states'] for a in sm[k]],
                                   attempts=[a['safety_limit']['action'] for a in sm[k]]),
                    note=("Both attempts of the instrumented run (60 s, then the 600 s rerun) were stopped by the safety limit with nothing collected; steps, restart cost, repeated work and the store vector are unavailable for this stage (AMENDMENTS 3.1), not 0. "
                          "The behaviour run reached the budget with the valid answer, so this is a limit of the measurement (PROTOCOL, Modes of running), not evidence about the model, and not a disagreement of semantic results between modes, since the cost/storage run reported nothing."
                          + (" In this configuration the behaviour run itself needed its 600 s rerun (attempt 1 timed out at 60 s)." if cfg == 'absys-depth-first' else ""))))

# ---------------------------------------------------------------- expressibility
EXPR = [
 ('P01a', None, "x = y, y = z, z = 2 are transcribed as equations; every token P; Absys holds an equation between unknowns natively."),
 ('P01b', 'conc(known, unknown, unknown)', "conc transcribed by its two cases in order (rule 3); the same definition serves this direction with no extra argument or case; no R tokens."),
 ('P01c', None, "x = [1&x] transcribes x = <1> ++ x directly; no R tokens. (The result is cyclic: complete under the rational reading, unsound under the finite one; that is an outcome, not expressibility.)"),
 ('P02a', None, "the three relations written as Absys 1 arithmetic assertions, which the core takes up in any direction once two of three numbers are known; no R tokens."),
 ('P02b', 'every order; R1 used to give v from u, R2 to give w from u and v (and held unsolved before), R3 to give u', "one text with a PART per relation, chosen by the harness's order; each relation is one primitive arithmetic assertion served in whichever direction the order needs; no R tokens, no control."),
 ('P02c', None, "R1, R2, R3 as one conjunction (begin ... end), in the problem's order; no R tokens."),
 ('P03a', 'conc(known, known, unknown)', "conc transcribed; forwards direction served by the transcription; no R."),
 ('P03b', 'conc(unknown, unknown, known): splitting', "the same transcription of conc serves the splitting direction (the core applies a lambda in any direction); no separate splitting function, no R."),
 ('P03c', 'conc(known, unknown, known): suffix', "same transcription; no R."),
 ('P03d', 'conc(unknown, known, known): prefix', "same transcription; no R."),
 ('P03e', 'rev(known, unknown)', "rev and conc transcribed by their cases with rev's conjuncts in the problem's order; no R."),
 ('P03f', 'rev(unknown, known)', "the same transcription of rev and conc, unchanged; no R and no control. It reports the one answer and then runs to the budget, which is an outcome (complete with budget), not a reformulation."),
]
expressibility = []
for cfg in CONFIGS:
    for sp, direction, reason in EXPR:
        expressibility.append(dict(configuration=cfg, subproblem=sp, direction=direction, expressibility='expressible',
            reason=reason + " Same text and same classes in all three configurations (no S mechanism in any: harnesses/absys/S-mechanisms.md)."))

out = dict(tokens=tokens_out, outcomes=outcomes, mode_differences=mode_diffs, expressibility=expressibility)
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('texts', len(tokens_out), 'tokens', sum(per_text.values()), dict(totals))
print('outcomes', len(outcomes), 'mode diffs', len(mode_diffs), 'expressibility', len(expressibility))
print('per text', per_text)
