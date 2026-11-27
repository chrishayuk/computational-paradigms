begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks, procedures (5.4), the for statement with a while element (4.6), conditional statements and expressions (3.3, 4.5) and the Boolean operator of negation (3.4), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), the message loop and observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of each relation until its unknown is known, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS a line 1: c, the integer of not (x = c). A line 2: d, the integer of x = d;
  comment P06a, and P06c, which has the same stages with other constants. One unknown x. Stage 1: not (x = c1). Stage 2: x = c2. x is a Boolean that says whether it has a value and an integer that holds it. Each relation is held as posed until x is known: then the equation gives x its value, or is tested, and the negation is tested. The negation of an equation whose unknown has no value is not decided: it is held;
  integer n, cap, m, i, code, k, c1, c2, xv, held, pass, x1, x2;
  Boolean xk, r1, r2, changed, inconsistent;

  procedure examine1;
  comment the evaluator of not (x = c1): with x known, it is tested. With x unknown, it waits;
  begin
    x1 := x1 + 1;
    if xk then
    begin if ¬(xv = c1) then r1 := false else begin inconsistent := true; r1 := false end end
  end examine1;

  procedure examine2;
  comment the evaluator of x = c2: with x known, it is tested, else x is given the value c2;
  begin
    x2 := x2 + 1;
    if xk then
    begin if ¬(xv = c2) then inconsistent := true end
    else
    begin xv := c2; xk := true; changed := true end;
    r2 := false
  end examine2;

  procedure propagate;
  comment every held relation is examined, in the order posed, again and again until a whole pass gives x no value;
  begin
    changed := true;
    for pass := 1 while changed do
    begin
      changed := false;
      if r1 then examine1;
      if r2 then examine2
    end
  end propagate;

  procedure relations;
  comment output adapter: the relations held, with the value of x put in its place if known;
  begin
    if r1 then begin outstring(1, "not (x = "); outinteger(1, c1); outstring(1, ")") end;
    if r2 then
    begin
      if r1 then outstring(1, ", ");
      outstring(1, "x = "); outinteger(1, c2)
    end
  end relations;

  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  xk := r1 := r2 := inconsistent := false;
  x1 := x2 := 0;

  for i := 1 while true do
  begin
    comment harness words: one message, the stage it poses, and then that stage's constants;
    ininteger(0, code); ininteger(0, k);
    if k = 1 then begin ininteger(0, c1); r1 := true end
    else if k = 2 then begin ininteger(0, c2); r2 := true end;

    propagate;

    comment the answer: x, and the relations still held;
    if ¬inconsistent then
    begin
      outstring(1, "[answer]x");
      if xk then begin outstring(1, " = "); outinteger(1, xv) end
      else if r1 ∨ r2 then outstring(1, " held") else outstring(1, " free");
      if r1 ∨ r2 then begin outstring(1, ", where "); relations end;
      outstring(1, "[/answer]\n")
    end;

    comment observe: the relations held, the value known, how many relations wait, and how often each was examined;
    held := (if r1 then 1 else 0) + (if r2 then 1 else 0);
    outstring(1, "[observe]");
    if inconsistent then outstring(1, "no solution\n");
    outstring(1, "held relations: ");
    if held = 0 then outstring(1, "none") else relations;
    outstring(1, "\n");
    if xk then begin outstring(1, "[bind x]"); outinteger(1, xv); outstring(1, "[/bind]\n") end;
    if held > 0 then
    begin outstring(1, "[suspended held-relations "); outinteger(1, held); outstring(1, "]\n") end;
    outstring(1, "[operations not-eq-examined "); outinteger(1, x1); outstring(1, "]\n");
    outstring(1, "[operations eq-examined "); outinteger(1, x2); outstring(1, "]\n");
    outstring(1, "[/observe]\n[end]")
  end
end
