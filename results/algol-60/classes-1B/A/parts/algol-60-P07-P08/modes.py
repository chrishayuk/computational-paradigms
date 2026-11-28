import json, glob
R="./"
def key(p):
    d=json.load(open(p)); out=[]
    for s in d["stages"]:
        a=s["attempts"][-1]; c=a["computations"][0]
        out.append(dict(stage=s["stage"], attempts=len(s["attempts"]), posed=a["posed"]["how"], states=c["execution_state"]["states"],
            answers=[x["verbatim"] for q in c["queries"] for x in q["answers"]], susp=c["suspended"]["items"], ops=c["problem_operations"],
            observe=a["observe"]["raw"], err=c["execution_state"]["error_verbatim"], safety=a["safety_limit"]["hit"]))
    return d, out
res=[]
for conf in ("report","x1"):
    for b in sorted(glob.glob(R+f"results/algol-60/{conf}/P0[78]/raw/*.behaviour.*.json")):
        inst=json.load(open(b))["run"]["instance"]
        db,kb=key(b)
        for mode in ("cost","storage"):
            ms=[p for p in glob.glob(R+f"results/algol-60/{conf}/P0[78]/raw/{inst}.{mode}.*.json")]
            assert len(ms)==1,(inst,mode,ms)
            dm,km=key(ms[0])
            diffs=[]
            for x,y in zip(kb,km):
                for f in x:
                    if x[f]!=y[f]: diffs.append((x["stage"],f,x[f],y[f]))
            if len(kb)!=len(km): diffs.append(("nstages",len(kb),len(km)))
            print(conf,inst,mode,ms[0].replace(R,""),"faults",dm["harness_faults"],"DIFFS" if diffs else "same", diffs[:5])
            # measurements
            for s in dm["stages"]:
                a=s["attempts"][-1]; c=a["computations"][0]
                st=c["steps"]
                print("    stage",s["stage"],"steps",st["stage"],"restated",st["restated"],"first",st["to_first_answer"],"end",st["to_end"],"rep",json.dumps(st["repeated_work"])[:120], "store",json.dumps(a["store"])[:200] if mode=="storage" else "")
