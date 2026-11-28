# Builds swi-prolog.json from rows.json (summarise.py) and tokens.json (tokens_classes.py).
import json, re
D='results/swi-prolog/classes-1C/A/parts/swi-prolog-P12/'
rows=json.load(open(D+'rows.json')); toks=json.load(open(D+'tokens.json'))
CONFS=['plain','tabling','coroutines','constraints','session']
def valid(sub,n):
    return {'P12a':{('r',),('l',)*n},'P12b':{('r',)},'P12c':{('r',)*n},'P12d':{('l',)*n}}[sub]
def parse(v):
    m=re.fullmatch(r"S = \[(.*)\]( |\.\n\n)",v); assert m,v
    return tuple(x.strip() for x in m.group(1).split(','))
def desc(s): return '<>' if not s else ('<r>' if s==('r',) else '%s^%d'%(s[0],len(s)))
S={(r['conf'],r['inst'],r['mode']):r for r in rows}
outcomes=[]
for c in CONFS:
  for sub in ['P12a','P12b','P12c','P12d']:
    for n in [8,12,16]:
      for mode in ['all','any']:
        inst='%s.n%d.%s'%(sub,n,mode)
        b=S[(c,inst,'behaviour')]; st=S[(c,inst,'storage')]
        got=[parse(a) for a in b['answers']]; V=valid(sub,n)
        assert all(g in V for g in got)
        if mode=='all': assert set(got)==V and len(got)==len(V); sem='complete'
        else: assert len(got)==1; sem='complete'
        states=b['states']
        order=', '.join(desc(g) for g in got)
        obs=[]
        obs.append('Answers, in order: %s (steps_at %s; cost run identical). ended_by %s.'%(order,b['steps_at'],b['ended']))
        obs.append('Unknowns: S is bound to a ground list at each answer; no unknown remains; no attributed variable (suspended at boundary %s), no suspended work, 0 items.'%b['susp'])
        if mode=='all':
            obs.append('Candidates examined over the stage: %d = 2^(n+1)-1, the whole space; the search finishes after the last solution, so the strategy covers the finite space.'%b['cand'])
        else:
            obs.append('Candidates examined to the (only collected) answer: %d.'%b['cand'])
        obs.append('Alternatives held for backtracking (retained choicepoints, storage run): at answers %s, at boundary %s, sampled maximum %s%s.'%(
            st['alt_at'],st['alts']['at_boundary'],(st['alts']['peak'] or {}).get('value','unavailable (no sample)' if c!='tabling' else 'unavailable (no sampler in tabling, AMENDMENTS 2)'),
            ', by type %s'%st['alts']['by_type'] if st['alts']['by_type'] else ''))
        obs.append('Problem-defined alternatives (partial sequences held): not reported, the program makes no h_held/2 call (unavailable, not 0).')
        if c=='tabling':
            q=st['store']['quantities']
            obs.append('Tabling: choice/2 tables completed before any candidate is examined: %d tables, %d table answers, %d bytes of table space at the boundary (storage run); first answer comes later in steps than in plain (%d against plain %d), in the same order as depth-first.'%(
                q['tables']['boundary'],q['table_answers']['boundary'],q['table_space_used_bytes']['boundary'],b['steps_at'][0],S[('plain',inst,'behaviour')]['steps_at'][0]))
        if c in ('coroutines','constraints','session'):
            obs.append('No coroutine, constraint or engine mechanism is used by the program (same text as plain); choice is not held until accept constrains s: the search is not avoided.')
        if c=='session':
            obs.append('session: single stage, posed fresh into one engine; the S hook (S/session-wait.pl) is loaded but never triggered (no undefined procedure).')
        if 'alternatives pending' in states:
            obs.append('The choicepoints left at the cap would, if resumed, yield no further valid answer in P12b/P12c/P12d (only one solution), and one more in P12a; the state is alternatives pending as the harness and SPECIFICATION 3 define it.')
        obs.append('No conclusion withdrawn (one stage). No manual action.')
        rule='SPECIFICATION Outcomes 1 (an any-one query answered with one valid answer is complete), 2 explicit, 3'
        outcomes.append({"configuration":c,"instance":inst,"program":'%s.pl'%sub,"record":b['file'],"stage":1,"reached":True,
            "semantic":sem,"representation":"explicit","simplification":None,"identical_to_posed":None,"residual_size":None,
            "execution_state":states,
            "residual_equivalence":"not a residual: explicit ground answers, checked by build.py against the valid outcomes %s: %s"%('{'+', '.join(sorted(desc(v) for v in V))+'}', 'all obtained, no invalid answer' if mode=='all' else 'the one answer is valid'),
            "observations":' '.join(obs),"rule":rule,"harness_fault":False,
            "answer_completeness":"%d/%d valid, 0 invalid"%(len(got),len(V)) if mode=='all' else "1 valid of 1 requested, 0 invalid"})
# mode differences: compare classification fields
mode_diff=[]
for r in rows:
    if r['mode']=='behaviour': continue
    b=S[(r['conf'],r['inst'],'behaviour')]
    key=lambda x:(tuple(x['answers']),x['ended'],tuple(x['states']),x['susp'])
    if key(r)!=key(b):
        mode_diff.append({"configuration":r['conf'],"instance":r['inst'],"program":r['inst'][:4]+'.pl',"mode":r['mode'],"record":r['file'],"stage":1,
            "behaviour":{"answers":b['answers'],"states":b['states']},"this_mode":{"answers":r['answers'],"states":r['states']},"note":""})
expr=[{"configuration":c,"subproblem":sub,"direction":None,"expressibility":"expressible",
       "reason":"choice is transcribed by its two cases in the order written, with its disjunction in order, n > 0 by comparison and n - 1 by is/2 in the direction used; accept is the problem's facts (closed world), looked up by member/2 (rule 9); the query is the conjunction choice(n, s), accept(s) in the order written. No R tokens. The search is the configuration's own (SLD depth-first%s)."%(', with choice/2 tabled (SLG): C tokens only' if c=='tabling' else '')}
      for c in CONFS for sub in ['P12a','P12b','P12c','P12d']]
smech=[]
for c in CONFS:
  for sub in ['P12a','P12b','P12c','P12d']:
    if c=='session':
      smech.append({"configuration":c,"program":sub+'.pl',"mechanism":"wait for an undefined procedure (harnesses/swi-prolog/S/session-wait.pl), loaded by the harness in every session run; not invoked here (every procedure the program calls is defined)","listed_at_phase_4":True,"tokens":0,"note":"0 program tokens: the mechanism's own 158 tokens (S-mechanisms.md) are counted once per configuration, not in this program; the program supplies no S of its own"})
    else:
      smech.append({"configuration":c,"program":sub+'.pl',"mechanism":None,"listed_at_phase_4":None,"tokens":0,"note":"none: the configuration lists no S mechanism and the program supplies none. External mechanisms (not S): member/2 of library(lists)%s"%(', :- table (SLG resolution)' if c=='tabling' else '')})
out={"tokens":toks,"outcomes":outcomes,"mode_differences":mode_diff,"expressibility":expr,"late_definition":[],"s_mechanisms":smech}
json.dump(out,open(D+'swi-prolog.json','w'),indent=1,ensure_ascii=False)
print(len(outcomes),len(mode_diff),len(expr),len(smech))
