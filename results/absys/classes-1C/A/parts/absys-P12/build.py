# Builds absys.json: outcomes from the records (behaviour runs classed in full; cost/storage compared),
# with the token spans from spans.py. Run: python3 -I spans.py && python3 -I build.py
import json, glob, os, re, collections
ROOT='./'
OUT='results/absys/classes-1C/A/parts/absys-P12/'
def valid(sub,n):
    L=['l']*n; R=['r']*n
    return {'P12a':[['r'],L],'P12b':[['r']],'P12c':[R],'P12d':[L]}[sub]
def parse_seq(txt):
    txt=txt.strip()
    assert txt.startswith('[') and txt.endswith(']'),txt
    inner=txt[1:-1]
    return [x.strip().strip("'") for x in inner.split(';')] if inner else []
recs=collections.defaultdict(dict)
for f in sorted(glob.glob(ROOT+'results/absys/*/P12/raw*/*.json*')):
    d=json.load(open(f)); r=d['run']
    recs[(r['configuration'],r['instance'])][r['mode']]=(os.path.relpath(f,ROOT),d)
def info(d):
    st=d['stages'][0]; at=st['attempts'][-1]; c=at['computations'][0]; q=c['queries'][0]
    ans=[]
    for a in q['answers']:
        m=re.search(r"\n    s = (.*)\n",a['verbatim']); ans.append(parse_seq(m.group(1)) if m else None)
    return st,at,c,q,ans
outcomes=[]; mode_diffs=[]
order={'absys':0,'absys-depth-first':1,'absys-wake-back':2}
def key(k):
    cfg,inst=k; sub,nn,mode=inst.split('.'); return (order[cfg],sub,int(nn[1:]),mode)
for k in sorted(recs,key=key):
    cfg,inst=k; sub,nn,am=inst.split('.'); n=int(nn[1:])
    path,d=recs[k]['behaviour']
    st,at,c,q,ans=info(d)
    V=valid(sub,n); cap=q['cap']
    states=c['execution_state']['states']
    fault=bool(d['harness_faults']) or path.endswith('.INVALID.json')
    # measured figures from the cost and storage runs of the same instance
    cp,cd=recs[k]['cost']; sp,sd=recs[k]['storage']
    _,_,cc,_,_=info(cd); _,sat,sc,_,_=info(sd)
    steps=cc['steps']['to_end']
    sq=sat['store']['quantities']
    pk=lambda name: (sq[name]['peak'] or {}).get('value') if name in sq else None
    held=c['alternatives']['held_as']
    prog=os.path.basename(d['run']['program']['path'])
    e=dict(configuration=cfg,instance=inst,program=prog,record=path,stage=1,reached=True)
    if 'timeout' in states:
        e.update(semantic='none reported',representation=None,simplification=None,identical_to_posed=None,residual_size=None,
          execution_state=['timeout'],residual_equivalence=None,
          observations=("Nothing reported: the repl was killed (SIGKILL) by the fixed 600 s safety limit of P12 while elaborating the stage's one assertion; "
            "no state was printed, observe.raw empty, bindings null; no rerun (P12 fixes the limit). The step budget (10^8) was not reported exhausted: steps, alternatives, suspended work and store are unavailable (not 0; AMENDMENTS 3.1), "
            "and the cost and storage runs of this instance were stopped the same way. Candidates examined: not counted by the harness (unavailable). "
            f"Alternatives held as {held}. No conclusion withdrawn (one stage). Manual actions: none. "
            "Timeout, not budget: P12's 'budget means the strategy did not cover it' does not apply; the configuration's wall time per step (all-live derivations) is what stopped it."),
          rule="SPECIFICATION Outcomes 1 (none reported) and 3 (timeout); PROTOCOL Running (safety limit; P12 limit fixed, not raised); AMENDMENTS 3.1")
    else:
        got=[a for a in ans]
        allv=sorted(map(tuple,V)); gots=sorted(map(tuple,got))
        if am=='all':
            sem='complete' if gots==allv else ('partial' if set(gots)<set(allv) and gots else 'unsound')
            compl=f"{len(set(gots)&set(allv))}/{len(allv)} valid answers, {len(set(gots)-set(allv))} invalid"
        else:
            ok=len(got)==1 and tuple(got[0]) in set(allv)
            sem='complete' if ok else 'unsound'
            compl=f"one answer asked for, {len(got)} collected, valid: {ok}"
        assert sem=='complete',(k,got)
        allprinted=d['stages'][0]['attempts'][-1]['observe']['raw'].count('derivation #')
        sl=lambda s:"<"+",".join(x.upper() for x in s)+">"
        orderrep=", ".join(sl(a) for a in got)
        e.update(semantic='complete',representation='explicit',simplification=None,identical_to_posed=None,residual_size=None,
          execution_state=['finished'],
          residual_equivalence=(f"Not a residual: each derivation binds s to a list of atoms and n to {n}, no relation left (no suspended process printed). "
            f"Collected s: {orderrep}; valid outcomes for {sub} at n={n}: {', '.join(sl(v) for v in V)}. "
            + ("Equal as sets (checked by build.py)." if am=='all' else
               f"An any-one query (cap 1): the one collected is valid; the state printed holds {allprinted} derivation(s), all valid.")),
          observations=(f"Answer completeness: {compl} (ended_by {q['ended_by']}). Unknowns: none remains unknown; s is bound to a list of quoted atoms in each derivation, n is the harness's parameter. "
            f"Alternatives at the boundary: {c['alternatives']['at_boundary']} derivation(s), one per solution, held as {held}; peak derivations {pk('derivations')} (sampled, every 1000 steps, storage run {sp}). "
            f"Suspended work: 0 at the boundary (store: susp_* peak {pk('susp_equations')}/{pk('susp_applications')}/{pk('susp_relations')}/{pk('susp_negations')}); pending peak {pk('pending')}, term_nodes peak {pk('term_nodes')}. "
            f"Steps to the end {steps} (cost run {cp}); every answer is reported at once at the end, so steps to the first answer = steps to the end. "
            f"Order of solutions reported: {orderrep}" + (f" (the first of {allprinted} printed derivations)" if am=='any' and allprinted>1 else "") + ". "
            "Candidates examined: not counted by the harness (unavailable). The system searched the space rather than avoiding it: accept did not hold choice back (steps grow with 2^n). "
            "Finished after the last solution: yes. No conclusion withdrawn (one stage). Manual actions: none."),
          rule="SPECIFICATION Outcomes 1 (complete; an any-one query answered by one valid answer is complete), 2 (explicit), 3 (finished); harness README 3.7 and QUESTIONS A8 (Absys never alternatives pending)")
    e['harness_fault']=fault
    outcomes.append(e)
    # mode comparison
    for m in ('cost','storage'):
        mp,md=recs[k][m]; _,mat,mc,mq,mans=info(md)
        same=(mans==ans and mc['execution_state']['states']==states and mq['ended_by']==q['ended_by'])
        if not same:
            mode_diffs.append(dict(configuration=cfg,instance=inst,program=prog,mode=m,record=mp,stage=1,
              behaviour=dict(answers=ans,execution_state=states),this_mode=dict(answers=mans,execution_state=mc['execution_state']['states']),note="differs"))
# expressibility
expr=[]
for cfg in order:
    for sub in ['P12a','P12b','P12c','P12d']:
        expr.append(dict(configuration=cfg,subproblem=sub,direction=None,expressibility='expressible with reformulation',
          reason=("choice's case 2 needs n > 0, a comparison no Absys notation has (systems/absys/README.md, Notation: P12's n > 0 named there). "
                  "The program replaces it by gtz, an enumeration q = 1 or ... or q = 16 (71 R tokens, plus the 4-token call), which equals q > 0 on every value choice is applied to "
                  "(n, n-1, ..., 0, with n in {8, 12, 16}); everything else (choice's two cases in order, n - 1 as an arithmetic relation, accept's closed-world facts, the query in order) is transcribed. "
                  "The meaning is kept on every input the problem states; it would not be for n > 16 (gtz(17) fails, so choice(17, s) would give only <>), which the problem does not pose. "
                  "Same text and same R tokens in all three configurations.")))
spans=json.load(open(OUT+'tokens.part.json'))
smech=[]
for cfg in order:
    for f in sorted(os.listdir(ROOT+'programs/absys/'+cfg)):
        if f.startswith('P12'):
            smech.append(dict(configuration=cfg,program=f,mechanism=None,listed_at_phase_4=True,tokens=0,
              note="No S mechanism: harnesses/absys/S-mechanisms.md lists none for this configuration, and the program supplies none (no hand-written search, scheduler or wait layer; the search is the configuration's own). gtz is R, not S: it is written for this problem's comparison, not a general mechanism."))
res=dict(tokens=spans,outcomes=outcomes,mode_differences=mode_diffs,expressibility=expr,late_definition=[],s_mechanisms=smech)
json.dump(res,open(OUT+'absys.json','w'),indent=1,ensure_ascii=False)
print(len(outcomes),'outcomes',len(mode_diffs),'mode diffs')
print(collections.Counter((o['configuration'],o['semantic'],tuple(o['execution_state'])) for o in outcomes))
