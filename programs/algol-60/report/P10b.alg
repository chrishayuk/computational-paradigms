begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for assignment statements (4.2), procedures (5.4), the for statement with a while element (4.6) and conditional statements (4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), the message loop and observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of a relation until its places are known, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS a line 1: f, of the relation d = f . b, at all times. A line 2: e, of b becomes e. A line 3: e, of b becomes b + e. A line 4: e, of b becomes e;
  comment P10b. Named quantities b and d, each an integer variable with a Boolean that says whether it has a value. Stage 1 poses the standing relation d = f . b, which is held, as posed, by a Boolean. Stages 2 to 4 replace the value of b by assignment, as in P10a. After every stage the standing relation, if posed, is examined: while b has no value it waits, and when b has one it gives d the value f . b, again after every stage, whatever value d had;
  integer n, cap, m, i, code, k, e, f, b, d, recomputed;
  Boolean bk, dk, r1;

  procedure examine1;
  comment the evaluator of the standing relation d = f . b, in the direction the problem defines it: d from b, whenever b has a value;
  if bk then
  begin d := f × b; dk := true; recomputed := recomputed + 1 end examine1;

  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  bk := dk := r1 := false; recomputed := 0;

  for i := 1 while true do
  begin
    comment harness words: one message, the stage it poses, and then that stage's constants;
    ininteger(0, code); ininteger(0, k);
    if k = 1 then
    begin comment d = f . b, at all times;
      ininteger(0, f); r1 := true end
    else if k = 2 then
    begin comment b becomes e;
      ininteger(0, e); b := e; bk := true end
    else if k = 3 then
    begin comment b becomes b + e;
      ininteger(0, e); b := b + e end
    else if k = 4 then
    begin comment b becomes e;
      ininteger(0, e); b := e end;

    if r1 then examine1;

    comment the answer: b and d, as their values, or held by the relation;
    outstring(1, "[answer]b");
    if bk then begin outstring(1, " = "); outinteger(1, b) end else if r1 then outstring(1, " held") else outstring(1, " has no value");
    outstring(1, ", d");
    if dk then begin outstring(1, " = "); outinteger(1, d) end else if r1 then outstring(1, " held") else outstring(1, " has no value");
    if r1 ∧ ¬bk then begin outstring(1, ", where d = "); outinteger(1, f); outstring(1, " . b") end;
    outstring(1, "[/answer]\n");

    comment observe: the standing relation, the values held, and how many times d has been recomputed;
    outstring(1, "[observe]");
    outstring(1, "standing relations: ");
    if r1 then begin outstring(1, "d = "); outinteger(1, f); outstring(1, " . b") end else outstring(1, "none");
    if r1 ∧ bk then outstring(1, ", examined after every stage, d recomputed from the value b has now");
    outstring(1, "\n");
    if bk then begin outstring(1, "[bind b]"); outinteger(1, b); outstring(1, "[/bind]\n") end;
    if dk then begin outstring(1, "[bind d]"); outinteger(1, d); outstring(1, "[/bind]\n") end;
    if r1 ∧ ¬bk then outstring(1, "[suspended held-relations 1]\n");
    outstring(1, "[operations d-recomputed "); outinteger(1, recomputed); outstring(1, "]\n");
    outstring(1, "[/observe]\n[end]")
  end
end
