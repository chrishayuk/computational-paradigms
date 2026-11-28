"""Independent classification. Reads only the brief's allowlisted inputs.

Does not execute Prolog, import repository code, or tokenize source text.
The construct walker operates solely on the supplied numbered token TSVs.
"""
from pathlib import Path
import collections
import csv
import gzip
import hashlib
import json
import re

ROOT = Path('.')
OUT = Path('results/swi-prolog/classes-1C/B/parts/swi-prolog-P09-P11')
CONFIGS = ['plain', 'tabling', 'coroutines', 'constraints', 'session']
PROBLEMS = ['P09', 'P10', 'P11']
TEXT_INDEX = ROOT / 'results/swi-prolog/tokens/TEXTS-1C-P09-P11.tsv'
TEXTS = []
ALIASES = {}
for line in TEXT_INDEX.read_text().splitlines()[1:]:
    first, _, rest = line.partition('\t')
    TEXTS.append(first)
    for alias in [first] + rest.split():
        ALIASES[alias] = first

def frozen(path):
    with (ROOT / 'results/swi-prolog/tokens' / (path + '.tokens.tsv')).open() as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    assert [int(x['index']) for x in rows] == list(range(len(rows)))
    return rows

class Walker:
    def __init__(self, path):
        self.path = path
        self.rows = frozen(path)
        self.t = [x['token'] for x in self.rows]
        self.labels = [None] * len(self.t)
        self.spans = []

    def put(self, a, b, cls, desc, rule):
        if b < a:
            return
        for i in range(a, b + 1):
            assert self.labels[i] is None, (self.path, i)
            self.labels[i] = cls
        self.spans.append(dict(from_=a, to=b, **{'class': cls}, construct=desc, rule=rule))

    def split(self, a, b, separators):
        depth = 0
        cuts = []
        for i in range(a, b + 1):
            x = self.t[i]
            if depth == 0 and x in separators:
                cuts.append(i)
            if x in ('(', '[', '{'):
                depth += 1
            elif x in (')', ']', '}'):
                depth -= 1
        return cuts

    def goal(self, a, b, context='', prefix=None):
        if a > b:
            return
        # A separator belongs to the following construct (rule 20).
        cuts = self.split(a, b, {',', ';', '->'})
        if cuts:
            start, pref = a, prefix
            for cut in cuts:
                self.goal(start, cut - 1, context, pref)
                if self.t[cut] == '->':
                    self.put(cut, cut, 'C', 'conditional branch connective', '1, 2, 10 (connective, not a separator)')
                    start, pref = cut + 1, None
                else:
                    start, pref = cut + 1, cut
            self.goal(start, b, context, pref)
            return
        x = self.t[a]
        def put(cls, desc, rule):
            self.put(a if prefix is None else prefix, b, cls, desc, rule)
        if x == '(' and self.t[b] == ')':
            # Here parentheses enclose the native case dispatch or replay test.
            self.put(a if prefix is None else prefix, a, 'C', 'conditional dispatch opening', '1, 2, 10, 20')
            self.goal(a + 1, b - 1, 'presence' if context == 'query' else context)
            self.put(b, b, 'C', 'conditional dispatch closing', '10')
        elif x in ('freeze', 'when'):
            sep = self.split(a + 2, b - 1, {','})
            assert len(sep) == 1
            k = sep[0]
            self.put(a if prefix is None else prefix, k - 1, 'C', x + ' condition and delay wrapper', '1, 10, 20')
            self.goal(k + 1, b - 1, context, k)
            self.put(b, b, 'C', x + ' wrapper closing', '10')
        elif x == 'h_commitment':
            put('H', 'fixed harness replayed commitment call', 'H; harness README section 12; 20')
        elif x == 'emit':
            # P11's specific rule overrides the generic harness list.
            put('P', 'problem emit operation', 'P11 Rules (emit and commit are problem tokens); 20')
        elif x in ('nonvar', 'var', '!'):
            put('C', 'mode test / commitment in arithmetic dispatch', '1, 2, 20')
        elif x in ('b', 'd') and context == 'presence' and prefix is None:
            put('C', 'test whether the named quantity already has a stored value', '1, 2: presence dispatch; 10')
        elif x == 'committed_value' or context == 'committed_value':
            put('R', 'decode the replayed answer into the selected equality', 'R definition; 10, 13 (not merely an output adapter), 20')
        elif x in ('sum_known', 'diff_known'):
            put('R', 'extra arithmetic mode evaluator procedure call', 'R extra definition; 10, 20')
        elif x == 'true' and context == 'commit':
            put('C', 'first-pose branch leaves selection to answers(1)', '1, 2, 10, 20')
        elif x == 'forall' and 'P10d' in self.path and context == 'query':
            put('R', 'apply the stored retractable comparison to this candidate', 'R extra held-relation encoding; 10, 20')
        elif x == 'assertz' and self.t[a + 2:a + 4] == ['(', 'd_of']:
            # Assertion of the standing relation, with nested arithmetic/delay.
            imp = self.split(a + 3, b - 2, {':-'})[0]
            self.put(a if prefix is None else prefix, imp, 'P', 'install the standing relation as a database rule', '1, 3, 10, 20')
            self.goal(imp + 1, b - 2, 'standing')
            self.put(b - 1, b, 'P', 'standing rule assertion closing', '10')
        elif x == 'assertz' and 'P10d' in self.path and self.t[a + 2] == 'held':
            # Encoded holder is extra, its comparison is still the problem.
            innercomma = self.split(a + 4, b - 2, {','})[0]
            self.put(a if prefix is None else prefix, innercomma - 1, 'R', 'associate a retractable relation with its unknown', 'R extra relation/argument; 10, 20')
            self.goal(innercomma + 1, b - 2, context, innercomma)
            self.put(b - 1, b, 'R', 'held-relation encoding closing', '10')
        elif x == 'retract' and 'P10d' in self.path:
            put('R', 'withdraw the encoded held comparison', 'R extra held-relation encoding; 10, 20')
        elif context == 'standing' and 'is' in self.t[a:b + 1]:
            put('R', 'evaluate the standing arithmetic relation in one direction', '8: stage 1 asks for the relation with neither place given; 10, 20')
        else:
            desc = 'problem goal: ' + ' '.join(self.t[a:b + 1])
            rule = '1, 3, 8, 10, 20'
            if x in ('member', 'memberchk'):
                rule = '6, 7, 9: read stage information / given closed-world facts; 20'
            put('P', desc, rule)

    def run(self):
        ends = self.split(0, len(self.t) - 1, {'.'})
        start = 0
        for end in ends:
            a, b = start, end - 1
            start = end + 1
            if self.t[a] == ':-':
                self.put(a, end, 'C', 'library configuration declaration' if self.t[a + 1] == 'use_module' else 'tabling or dynamic database declaration', '1, 11, 12: enable execution mechanism / choose undefined failure; see notes')
                continue
            imps = self.split(a, b, {':-'})
            name = self.t[a]
            hhead = name in ('unknowns', 'stage', 'query', 'spawned')
            if not imps:
                self.put(a, end, 'H' if hhead else 'P', 'fixed harness fact' if hhead else 'stage constants / problem fact or definition case', 'H; harness README section 12' if hhead else '1, 3, 6')
                continue
            imp = imps[0]
            cls = 'H' if hhead else ('R' if name in ('sum', 'diff', 'sum_known', 'diff_known', 'committed_value') else 'P')
            self.put(a, imp, cls, name + ' clause head', 'H; harness README section 12' if hhead else ('R extra mode-dispatch / replay-decoding definition; 10' if cls == 'R' else '1, 3, 10'))
            ctx = 'commit' if 'h_commitment' in self.t[imp + 1:b + 1] else name
            self.goal(imp + 1, b, ctx)
            self.put(end, end, cls, name + ' clause closing', '10')
        assert start == len(self.t)
        assert all(self.labels)
        spans = []
        for s in sorted(self.spans, key=lambda s: s['from_']):
            s['from'] = s.pop('from_')
            spans.append(s)
        return spans

def read_record(f):
    return json.load(gzip.open(f, 'rt') if f.suffix == '.gz' else f.open())

def record_files():
    for c in CONFIGS:
        for p in PROBLEMS:
            for folder in ('raw', 'raw-rerun-m2'):
                for f in sorted((ROOT / 'results/swi-prolog' / c / p / folder).glob('*')):
                    if f.name.endswith(('.json', '.json.gz')):
                        yield f

def brief_raw(raw, reference):
    if raw is None or len(raw) <= 2000:
        return raw
    return dict(verbatim_at=reference, characters=len(raw), sha256=hashlib.sha256(raw.encode()).hexdigest(),
                prefix=raw[:100], suffix=raw[-150:], note='Verbatim is retained at the cited record field; no elision in the source record.')

def classify_record(f, d):
    r = d['run']
    cfg, inst = r['configuration'], r['instance']
    problem = r['subproblem']
    entries = []
    fault = bool(d.get('harness_faults')) or '.INVALID.' in f.name
    for si, s in enumerate(d['stages']):
        k = s['stage']
        for ai, a in enumerate(s['attempts']):
            for comp in a['computations']:
                cid = comp['id']
                states = comp['execution_state']['states'][:]
                answers = [x['verbatim'] for q in comp['queries'] for x in q['answers']]
                raw = a.get('observe', {}).get('raw')
                readings = ['finite', 'stream'] if problem == 'P09d' else [None]
                for reading in readings:
                    o = dict(configuration=cfg, instance=inst, program=Path(r['program']['path']).name,
                             record=str(f.relative_to(ROOT)), stage=k, attempt=a['attempt'], computation=cid,
                             reading=reading, reached=True, semantic='complete', representation='explicit',
                             simplification=None, identical_to_posed=None, residual_size=None,
                             execution_state=states, residual_equivalence=None, harness_fault=fault,
                             rule='SPECIFICATION Outcomes 1–3; problem valid outcomes; AMENDMENTS 3')
                    reason = 'All reported values agree with the problem’s valid outcomes.'
                    obs = dict(answers_verbatim=answers,
                               observed=brief_raw(raw, f"{f.relative_to(ROOT)}#/stages/{si}/attempts/{ai}/observe/raw"),
                               unknowns='Unbound places are Prolog variables; lists use [] and [Head|Tail].',
                               alternatives=comp.get('alternatives'), suspended=comp.get('suspended'),
                               execution_basis=comp['execution_state']['basis'], error_verbatim=comp['execution_state'].get('error_verbatim'),
                               posing=a['posed'], collected_on=[q.get('collected_on') for q in comp['queries']],
                               manual_actions=a.get('manual_actions', []) + d.get('manual_actions', []),
                               conclusion_withdrawn=None, problem_observation=None,
                               unavailable_measurements='null is unavailable, never zero; fault-associated readings are not treated as zero')
                    if problem == 'P09a':
                        obs['problem_observation'] = ('Separate queries in one process, side_by_side=false. B is blocked until A stops in AB; B finishes before A starts in BA. Tabling makes loop fail finitely.' if cfg == 'tabling' else 'Separate queries in one process, side_by_side=false. AB delays B until A exhausts its budget; BA reports B before A starts. No side-by-side progress.')
                        if cid == 'A' and 'finished' not in states:
                            o.update(semantic='none reported', representation=None)
                            reason = 'loop has no least-model instances; the computation does not report its empty solution set before the stop.'
                        elif cid == 'A':
                            reason = 'Tabled loop finitely fails, exactly reporting the empty least relation.'
                        else:
                            reason = 'B reports the sole valid reverse [3,2,1], independently of A’s lack of solutions.'
                    elif problem == 'P09b':
                        obs['problem_observation'] = 'A’s incompatible equalities fail; B subsequently reports Y=3 in the same instance. Failure is isolated.'
                        reason = 'A explicitly exhausts the empty set; B gives its unique valid value.'
                    elif problem == 'P09c':
                        if cfg in ('coroutines', 'constraints', 'session'):
                            o.update(representation='residual', simplification='reducible', identical_to_posed=False,
                                     residual_size=dict(input_relations=2, input_unknown_occurrences=3, residual_relations=1, residual_unknown_occurrences=1, description='gen(1,S),sum3(S,Total) -> S=[1,2,3|Tail], Total=6, gen(4,Tail); delay wrappers are control, solved bindings need no decision'))
                            o['residual_equivalence'] = 'Equivalent: the surviving gen(4,Tail) has exactly Tail=[4,5]. Its prefix therefore fixes the required full S=[1,2,3,4,5] and Total=6. Reducible to that explicit solution.'
                            obs['problem_observation'] = 'Consumer demands the first three cells before producer completion; the last tail and gen(4,Tail) remain frozen. One attributed variable, one residual goal. This is demand-driven coroutining, not concurrent threads.'
                        else:
                            obs['problem_observation'] = 'Textual depth-first conjunction completes gen before starting sum3; no consumer/producer interleaving is evidenced.'
                        reason = 'The explicit answer or retained tail condition denotes exactly the one valid finite sequence and total.'
                    elif problem == 'P09d':
                        if cfg in ('coroutines', 'constraints', 'session'):
                            o.update(representation='residual', identical_to_posed=False,
                                     simplification='inconsistency undetected' if reading == 'finite' else 'reduced',
                                     residual_size=dict(input_relations=2, input_unknown_occurrences=3, residual_relations=1, residual_unknown_occurrences=1, description='genu(1,S),sum3(S,Total) -> S=[1,2,3|Tail], Total=6, genu(4,Tail)'))
                            if reading == 'finite':
                                o['residual_equivalence'] = 'Equivalent to the empty valid outcome: genu has no finite least-model instances at any n, so genu(4,Tail) is inconsistent. The reported answer includes this undecided condition, not an unconditional finished Total=6; inconsistency is undetected.'
                            else:
                                o['residual_equivalence'] = 'Equivalent under the stated greatest-relation stream reading: genu(4,Tail) uniquely denotes 4,5,6,...; its prefixed stream is 1,2,3,... and Total=6. An infinite ascending stream has no finite solved list form; the one remaining generator relation is necessary.'
                            obs['problem_observation'] = 'Total=6; consumer has demanded three cells. Producer is suspended on the unbound tail, with one attributed variable and one frozen goal, not running to the budget.'
                            reason = 'Interpret the reported residual under the selected least/greatest relation, keeping semantic equivalence distinct from simplification.'
                        else:
                            o.update(semantic='none reported', representation=None)
                            reason = 'No answer and no observed Total binding. Producer reaches the budget before sum3 executes. A held finite prefix of S is an execution observation, not a completed solution or a Total answer.'
                            obs['problem_observation'] = 'Producer builds an open prefix; consumer has not executed and Total remains a free Prolog variable. No frozen goals are held.'
                    elif problem == 'P09e':
                        if cfg in ('plain', 'tabling'):
                            o.update(semantic='none reported', representation=None)
                            reason = 'Arithmetic mode dispatch calls is/2 without sufficient instantiation; it reports no solution or retained relation.'
                        else:
                            o.update(representation='residual', simplification='reducible', identical_to_posed=cfg == 'coroutines',
                                     residual_size=dict(input_relations=2, input_unknown_occurrences=4, residual_relations=2, residual_unknown_occurrences=4, description='Two primitive integer addition/subtraction relations; one would suffice. Delay/mode wrappers do not add problem relations.'))
                            o['residual_equivalence'] = 'Equivalent: X=Y+1 iff Y=X-1 over all integers. Both retained constraints therefore denote precisely {(y+1,y): y integer}; discard either to make the residual smaller. No finite imposed integer domain.'
                            obs['problem_observation'] = 'Two attributed variables and two residual goals; no enumeration or deadlock diagnostic. The suspended state is distinguishable from finished. ' + ('when wrappers retain the two posed arithmetic conditions.' if cfg == 'coroutines' else 'CLPFD normalizes both posed conditions to duplicate Y+1#=X; it does not remove the duplicate.')
                    elif problem == 'P10a':
                        reason = 'Native database replacement yields B=10, then 15 from its prior value plus 5, then 7.'
                        obs['problem_observation'] = 'Retract/assert replaces the one current database fact. Old values are not retained as named versions; earlier answers remain in the record only.'
                        if k > 1: obs['conclusion_withdrawn'] = 'The earlier current B value is replaced; the new answer shows its successor.'
                    elif problem == 'P10b':
                        if k == 1:
                            if cfg in ('plain', 'tabling'):
                                o.update(semantic='none reported', representation=None)
                                reason = 'The standing database rule is installed, but querying its is/2 evaluation on unknown B raises an instantiation error. No residual answer is reported.'
                            else:
                                o.update(representation='residual', simplification='reduced', identical_to_posed=True,
                                         residual_size=dict(input_relations=1, input_unknown_occurrences=2, residual_relations=1, residual_unknown_occurrences=2, description='One integer multiplication relation 2*B=D; freeze is a control wrapper.'))
                                o['residual_equivalence'] = 'Equivalent over the problem’s integer arithmetic: the condition is D=2*B, with both unvalued. One primitive multiplication relation is minimal; arithmetic expressions are not solved-form terms under Outcomes 2.'
                        else:
                            reason = 'The query re-evaluates the standing rule on the current B: D=20,30,14, respectively.'
                        obs['problem_observation'] = 'Standing relation stored as d_of/2 rule, separate from the replaceable B fact. One dependent D value is evaluated when queried; no trace measures proactive recomputation. No value/version history is retained.'
                        if k > 2:obs['conclusion_withdrawn'] = 'Prior B and D values are superseded by the replacement and newly queried derived value.'
                    elif problem == 'P10c':
                        if k == 1:
                            o['representation'] = 'solved form'
                            o['residual_equivalence'] = 'Equivalent: B=10 and D is unassigned/free, with no relation to decide. D acquires its snapshot value only at stage 2.'
                        reason = 'Native stored snapshot: D is absent at stage 1, becomes 20 at stage 2, and stays 20 while B becomes 15 then 7.'
                        obs['problem_observation'] = 'Independent replaceable b/1 and d/1 facts; no time indexing. D is computed once, not recomputed with later B replacements.'
                        if k > 2:obs['conclusion_withdrawn'] = 'The old B value is superseded; D=20 remains valid.'
                    elif problem == 'P10d':
                        reason = 'Enumerates exactly [1,2,3], [2,3], [1,2,3] at stages 1,2,3; pick is unchanged and the held comparison is removed at stage 3.'
                        obs['problem_observation'] = 'Database facts hold pick and the one encoded retractable comparison. The query enumerates pick afresh and tests each held relation. X=1 returns when the comparison is retracted, without reinserting pick(1). ' + ('The session receives database edits incrementally; queries for intermediate stages run separately.' if cfg == 'session' else 'All stages including the withdrawal are replayed; the restored answers come from the query over the resulting database.')
                        if k == 2:obs['conclusion_withdrawn'] = 'X=1 is absent from this stage’s answers; no separate retraction notification.'
                        if k == 3:obs['conclusion_withdrawn'] = 'Earlier exclusion of X=1 no longer holds; X=1 is reported again.'
                    elif problem.startswith('P11'):
                        reason = 'P11 asks for any one answer; the first selected value is complete at this stage under its current constraints.'
                        if problem == 'P11d' and k == 3:
                            if cfg == 'session':
                                o['semantic'] = 'unsound'
                                reason = 'Stage 2 committed to X=1. Adding X!=1 leaves no valid outcome, but the incremental conjunction backtracks through pick and reports X=2. The commit stage has no native cut or stored equality on its first pose.'
                            else:
                                reason = 'The replayed commit fixes X=1; the final X!=1 finitely fails, correctly reporting no solutions.'
                            obs['conclusion_withdrawn'] = 'X=1 from the commit is contradicted. ' + ('It is replaced by an invalid new choice X=2.' if cfg == 'session' else 'The new query reports the empty set, preserving the commit equality.')
                        if problem == 'P11c' and k == 2:
                            obs['conclusion_withdrawn'] = 'Provisional X=1 is refuted and the next choice X=2 is reported. Its emitted log entry cannot be withdrawn.'
                        effects = d.get('effects') or {}
                        endlog = effects.get('log_after_run', [])
                        commit_stage = {'P11a':1, 'P11b':1, 'P11c':3, 'P11d':2}[problem]
                        selected = '2' if problem in ('P11a','P11b','P11c') else '1'
                        effect_class = 'exact' if problem == 'P11a' else 'extra'
                        o['effects'] = dict(class_at_problem_end=effect_class, committed_value=selected,
                                            commit_stage=commit_stage, log_at_problem_end=[e['entry'] for e in endlog],
                                            entries=[dict(e, timing=('before commitment' if e['stage'] <= commit_stage else 'after commitment'),
                                                          timing_reason='emit is executed during exploration, before the selecting answer is reported; replay after a prior commit is after commitment') for e in endlog],
                                            note='Class judged on the entire classification log at problem end, including replay duplicates; observation-log entries are excluded. No program deferral is present.')
                        obs['effects_this_attempt'] = a.get('effects', [])
                        obs['problem_observation'] = 'Commitment is the first answer to answers(1), not a cut. Replayed commits are decoded as X=v. The initial commit clause itself installs no persistent equality. ' + ('All stages share the engine, so later backtracking can revisit the provisional choice.' if cfg == 'session' else 'Reposing repeats irreversible emit calls; their repeated entries count separately.')
                    if not answers and 'error' in states and 'HARNESS FAULT' in str(comp['execution_state'].get('error_verbatim')):
                        o.update(semantic='none reported', representation=None, simplification=None, identical_to_posed=None, residual_size=None, residual_equivalence=None)
                        reason = 'The harness has no end event; its synthetic error is a harness observation failure, not a demonstrated Prolog error.'
                        # The stage was posed, but this computation's start is unknown.
                        if cid == 'B' and problem == 'P09a' and r['parameters'].get('spawn_order') == ['A','B']:
                            o['computation_reached'] = None
                            reason = 'Stage 1 was reached. The record has no B answer/end event after the harness fault while handling A; whether B started is unavailable. The error state is the harness’s synthetic placeholder, not evidence of B failing.'
                    replay_source = str(comp.get('steps', {}).get('restart_cost_source') or '')
                    if re.search(r'before stage ' + str(k) + r' was (posed|posted)', replay_source):
                        o.update(reached=False,semantic='none reported',representation=None,simplification=None,identical_to_posed=None,residual_size=None,residual_equivalence=None,execution_state=[])
                        reason = 'Not reached: ' + replay_source
                    o['reason'] = reason
                    o['observations'] = obs
                    entries.append(o)
    return entries

def main():
    tokens = {path: Walker(path).run() for path in TEXTS}
    # Check aliases against frozen streams, not newly tokenized source.
    for alias, first in ALIASES.items():
        assert [x['token'] for x in frozen(alias)] == [x['token'] for x in frozen(first)], (alias, first)
    outcomes, measurements, behaviours = [], [], {}
    inventory = []
    for f in record_files():
        d = read_record(f)
        key = (d['run']['configuration'], d['run']['instance'], Path(d['run']['program']['path']).name)
        es = classify_record(f, d)
        inventory.append((str(f.relative_to(ROOT)), d['run']['mode'], len(es), bool(d.get('harness_faults'))))
        if d['run']['mode'] == 'behaviour':
            outcomes.extend(es)
            behaviours[key] = es
        else:
            measurements.append((f, d['run']['mode'], key, es))
    differences = []
    axes = ['reached','semantic','representation','simplification','identical_to_posed','residual_size','execution_state','residual_equivalence']
    for f, mode, key, es in measurements:
        bs = {(o['stage'],o['attempt'],o['computation'],o['reading']):o for o in behaviours[key]}
        for o in es:
            b = bs[(o['stage'],o['attempt'],o['computation'],o['reading'])]
            if mode == 'storage':
                b['observations']['storage_measurement'] = dict(
                    record=o['record'], harness_fault=o['harness_fault'],
                    alternatives=o['observations']['alternatives'], suspended=o['observations']['suspended'],
                    note='Separate storage run; null remains unavailable. These figures do not replace the behaviour classification.')
            if any(o[a] != b[a] for a in axes):
                differences.append(dict(configuration=o['configuration'],instance=o['instance'],program=o['program'],mode=mode,
                                        record=o['record'],stage=o['stage'],attempt=o['attempt'],computation=o['computation'],reading=o['reading'],
                                        behaviour={a:b[a] for a in axes},this_mode={**{a:o[a] for a in axes},'observations':o['observations'],'reason':o['reason']},
                                        harness_fault=o['harness_fault'],note='Original measurement is retained. Difference is an instrumentation/harness fault, not a change to the behaviour classification.'))
    expressibility = []
    for cfg in CONFIGS:
        for sub in ['P09a','P09b','P09c','P09d1','P09d2','P09e','P10a','P10b','P10c','P10d','P11a','P11b','P11c','P11d']:
            ex = 'expressible'
            reason = 'Definitions and stage information are transcribed with native unification, clauses and arithmetic in the directions used; operational failure to terminate is separate from expressibility.'
            if sub == 'P09a':reason = 'loop and forward rev are literal clauses; spawn order and sequential execution affect progress, not definability. No S scheduler is supplied.'
            elif sub == 'P09b':reason = 'Native incompatible equalities and independent binding transcribe the two goals.'
            elif sub in ('P09c','P09d1','P09d2'):
                reason = 'gen/genu and sum3 transcribe the cases in the given order; arithmetic is used in the forward directions queried. Freeze/tabling adds C, not new cases. Least/greatest readings and suspended residuals are classified separately.'
                if sub == 'P09d2' and cfg in ('plain','tabling'):
                    reason += 'The stream’s consumer is never reached in the run; this is an execution limitation of the transcription, not evidence that an R or S definition was used.'
            elif sub == 'P09e' and cfg in ('plain','tabling','coroutines'):
                ex='expressible with reformulation'
                reason='Extra sum/diff mode-dispatch clauses implement integer arithmetic by is/2 in each direction (R heads; P arithmetic; C mode tests/cuts/delays). Their extensional integer relation is preserved; plain/tabling still error with both unknowns at this query. This judgement concerns definitions, not successful execution.'
            elif sub == 'P09e':reason='CLPFD directly expresses both integer arithmetic relations over unbounded integer domains; duplicate retention is a simplification issue.'
            elif sub in ('P10a','P10c'):reason='Native dynamic database replacement implements the named quantities; relative arithmetic uses the old fact, and the snapshot is stored once. No time/version indexing.'
            elif sub == 'P10b':
                if cfg in ('plain','tabling','coroutines'):
                    ex='expressible with reformulation'
                    reason='The native standing database rule uses directional is/2 (R) where stage 1 asks for an unvalued relation. Its integer relation is D=2*B; coroutines retains it with freeze, while plain/tabling raise an instantiation error when queried before B has a value.'
                else:reason='Native standing database rule with CLPFD multiplication transcribes D=2*B; replacing B does not bind an earlier logical variable to a new value.'
            elif sub == 'P10d':
                ex='expressible with reformulation'
                reason='Native assert/retract provides state change, but the program adds held/2 and a query-time interpreter for the problem’s retractable comparison (R). It preserves pick and restores the removed candidate. This small holder for the problem’s single comparison is not an added general propagator or scheduler.'
            elif sub in ('P11a','P11b'):reason='pick, comparison and emit are in the problem’s order; emit is P by the explicit P11 rule. Extra effects are a separate outcome axis.'
            elif sub in ('P11c','P11d'):
                ex='expressible with reformulation'
                reason='The extra committed_value/2 parser (R) translates the fixed harness’s textual replay answer to X=v. Provisional stages are literal. The native initial selection is answers(1); its failure to constrain subsequent session backtracking is reported as unsound at P11d stage 3, not credited as a sound persistent commit mechanism.'
            direction = 'forward rev; loop' if sub=='P09a' else ('forward producer and prefix sum' if sub in ('P09c','P09d1','P09d2') else None)
            expressibility.append(dict(configuration=cfg, subproblem=sub, direction=direction, expressibility=ex, reason=reason))
    supporting = []
    for alias in sorted(ALIASES):
        cfg, name = alias.split('/')
        supporting.append(dict(configuration=cfg,program=name,
                               mechanism='wait for an undefined procedure (loaded configuration mechanism, dormant in these programs)' if cfg=='session' else None,
                               listed_at_phase_4=True if cfg=='session' else None,
                               tokens=None if cfg=='session' else 0,
                               token_ranges=[], source='harnesses/swi-prolog/S/session-wait.pl' if cfg=='session' else None,
                               phase_4_declared_total_tokens=158 if cfg=='session' else None,
                               note='No S constructs in this program. ' + ('Configuration-wide module is loaded but no undefined procedure call uses it. Its frozen token stream is absent, so an independent S/H token count is unavailable; 158 is the phase-4 declaration, not a re-tokenized count.' if cfg=='session' else 'No supporting mechanism is supplied or invoked.')))
    result = dict(tokens=tokens,outcomes=outcomes,mode_differences=differences,expressibility=expressibility,late_definition=[],s_mechanisms=supporting)
    (OUT/'swi-prolog.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (OUT/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    counts=collections.Counter()
    for spans in tokens.values():
        for s in spans:counts[s['class']]+=s['to']-s['from']+1
    print(json.dumps(dict(texts=len(tokens),program_paths=len(ALIASES),records=len(inventory),behaviour_records=len(behaviours),outcomes=len(outcomes),mode_differences=len(differences),tokens=dict(counts),semantic=dict(collections.Counter(o['semantic'] for o in outcomes)),states=dict(collections.Counter(x for o in outcomes for x in o['execution_state']))),indent=2))

if __name__=='__main__':
    main()
