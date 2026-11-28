import json, glob, os
R="./"
rows={}
for conf in ("report","x1","x1sim"):
    for p in sorted(glob.glob(R+f"results/algol-60/{conf}/P0[78]/raw/*.behaviour.*.json")):
        d=json.load(open(p))
        inst=d["run"]["instance"]
        st=[]
        for s in d["stages"]:
            a=s["attempts"][-1]
            c=a["computations"][0]
            st.append((s["stage"], len(s["attempts"]), a["posed"]["how"], tuple(c["execution_state"]["states"]), tuple(x["verbatim"] for q in c["queries"] for x in q["answers"]), json.dumps(c["suspended"]["items"]), a["observe"]["raw"].replace("+","").replace(" ","")[:400], c["execution_state"]["error_verbatim"], a["exit"]["status"], json.dumps(c["problem_operations"])))
        rows[(conf,inst)]=(p.replace(R,""),st,d["harness_faults"],d["manual_actions"],d["run"]["posing"])
insts=sorted(set(i for c,i in rows))
for i in insts:
    r=rows[("report",i)]
    for conf in ("x1","x1sim"):
        x=rows.get((conf,i))
        if not x: print("missing",conf,i); continue
        for a,b in zip(r[1],x[1]):
            if a[:4]!=b[:4] or a[5]!=b[5] or a[9]!=b[9] or [s.replace(" ","") for s in a[4]]!=[s.replace(" ","") for s in b[4]]:
                print("DIFF",conf,i,a[:6],b[:6])
        print(conf,i,x[0],x[2],x[3],x[4],[ (s[0],s[1],s[2],s[3],s[7],s[8]) for s in x[1]])
