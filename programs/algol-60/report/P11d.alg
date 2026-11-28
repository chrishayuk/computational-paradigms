begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays (5.2), procedures and function designators (5.4), the for statement with step-until and while elements (4.6) and conditional statements and expressions (3.3, 4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), the effect stub emit bound as printing and the replayed commitment read back as an integer (harnesses/algol-60/README.md, 2.2 and 2.5), the message loop and observe block of the harness README example X01 (2.8), and the holding of each relation posed after pick, and of the position reached in pick's facts, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS a line 1: F f1 ... fF, the number of facts of pick and then the value of each fact, in order. Stage 2, commit, has no constants. A line 3: c, the integer of x different from c;
  comment P11d. One unknown x, and queries for any one outcome. Stage 1: pick(x) and emit(x). Stage 2: commit. Stage 3: x different from c3. pick is given by its facts, tried in order, one at a time: a fact gives x its value, emit(x) is carried out, as the conjunct that follows pick in stage 1, and then every relation posed since is tested, in the order posed. The first fact that passes them all is the outcome reported, and the facts after it are kept, untried. When a later stage refutes the outcome, the next facts are tried in the same way. Commit selects the outcome held and adds the information x = v, held as one more relation. A replayed commitment, the message 3, gives v, which is read back and added in the same way. An answer, and the entry emitted, is x alone, its digits printed with no spaces;
  integer n, cap, m, i, code, k, j, nf, c3, xv, cur, cv, untried;
  Boolean picked, xk, committed, r3;
  integer array fv[1:1000], pk[1:1000];

  Boolean procedure holds(x);
    value x; integer x;
  comment the relations posed after pick(x) and emit(x), tested on x in the order posed: x = v, once the commitment is made, and x different from c3, once stage 3 is posed;
  holds := (if committed then x = cv else true) ∧ (if r3 then x ≠ c3 else true);

  procedure num(v);
    value v; integer v;
  comment output adapter: an integer, a minus sign if it is negative and then its decimal digits, with no spaces;
  begin
    integer d;
    if v < 0 then begin outstring(1, "-"); num(-v) end
    else
    begin
      if v ≥ 10 then num(v ÷ 10);
      d := v - v ÷ 10 × 10;
      if d = 0 then outstring(1, "0") else if d = 1 then outstring(1, "1") else if d = 2 then outstring(1, "2")
      else if d = 3 then outstring(1, "3") else if d = 4 then outstring(1, "4") else if d = 5 then outstring(1, "5")
      else if d = 6 then outstring(1, "6") else if d = 7 then outstring(1, "7") else if d = 8 then outstring(1, "8")
      else outstring(1, "9")
    end
  end num;

  procedure emit(v);
    value v; integer v;
  comment the effect stub emit(v) of the harness, bound as printing;
  begin outstring(1, "[emit]"); num(v); outstring(1, "[/emit]\n") end emit;

  procedure advance;
  comment the facts of pick after the current one, tried in order until one passes: each gives x its value, emit(x) is carried out, and the relations posed since are tested. If none passes, x has no value;
  begin
    Boolean ok;
    ok := false;
    for j := 0 while ¬ok ∧ cur < nf do
    begin
      cur := cur + 1; pk[cur] := pk[cur] + 1;
      xv := fv[cur];
      emit(xv);
      ok := holds(xv)
    end;
    xk := ok
  end advance;

  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  picked := xk := committed := r3 := false; nf := cur := 0;

  for i := 1 while true do
  begin
    comment harness words: one message, the stage it poses, replays or replays as a commitment, and then, for a commitment, its value v;
    ininteger(0, code); ininteger(0, k);
    if code = 3 then
    begin
      comment the replayed commit stage, as the information x = v;
      ininteger(0, cv); committed := true
    end
    else if k = 1 then
    begin
      comment pick(x) and emit(x): pick's facts, then the first of them;
      ininteger(0, nf);
      for j := 1 step 1 until nf do begin ininteger(0, fv[j]); pk[j] := 0 end;
      picked := true; cur := 0;
      advance
    end
    else if k = 2 then
    begin
      comment commit: the outcome held is selected, and x = v is added;
      if xk then begin cv := xv; committed := true end
    end
    else if k = 3 then begin ininteger(0, c3); r3 := true end;

    comment the outcome held, if a relation posed at this stage refutes it, is replaced by the next fact that passes;
    if xk then begin if ¬holds(xv) then advance end;

    comment the answer: the one outcome held;
    if xk then begin outstring(1, "[answer]"); num(xv); outstring(1, "[/answer]\n") end;

    comment observe: the outcome, the relations held, the commitment, the facts of pick tried and untried;
    untried := if picked then nf - cur else 0;
    outstring(1, "[observe]");
    if picked ∧ ¬xk then outstring(1, "no solution\n");
    if xk then begin outstring(1, "[bind x]"); num(xv); outstring(1, "[/bind]\n") end;
    outstring(1, "relations after pick and emit: ");
    if ¬committed ∧ ¬r3 then outstring(1, "none");
    if committed then begin outstring(1, "x = "); num(cv); outstring(1, " (committed)") end;
    if r3 then begin if committed then outstring(1, ", "); outstring(1, "not (x = "); num(c3); outstring(1, ")") end;
    outstring(1, "\n");
    if picked then
    begin
      outstring(1, "facts of pick tried: "); num(cur); outstring(1, " of "); num(nf);
      outstring(1, ", untried and kept for a later stage: "); num(untried); outstring(1, "\n");
      outstring(1, "[held-as backtracking]\n");
      outstring(1, "[problem-alternatives x "); outinteger(1, (if xk then 1 else 0) + untried); outstring(1, "]\n")
    end;
    for j := 1 step 1 until nf do
    begin outstring(1, "[operations pick/"); num(j); outstring(1, " "); outinteger(1, pk[j]); outstring(1, "]\n") end;
    outstring(1, "[/observe]\n[end]")
  end
end
