begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks, procedures (5.4), the for statement with a while element (4.6), conditional statements and expressions (3.3, 4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of each relation until enough of its places are known, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS a line 1: c1 c2, the integers of R1, x + y = c1, and R2, x - y = c2;
  comment P07b. Integer unknowns x, y. One stage: R1, then R2. Each unknown is a Boolean that says whether it has a value and an integer that holds it. Each relation is held as posed until one of its unknowns is known, when it gives the other its value, or until both are, when it is tested. Every held relation is examined in the order posed, again and again, until a whole pass gives no unknown a value. The relations are not solved together: no relation acts while both its unknowns are unknown;
  integer n, cap, m, i, code, k, c1, c2, xv, yv, held, pass, x1, x2;
  Boolean xk, yk, r1, r2, changed, inconsistent;

  procedure examine1;
  comment the evaluator of R1, x + y = c1;
  begin
    x1 := x1 + 1;
    if xk ∧ yk then
    begin if xv + yv ≠ c1 then inconsistent := true; r1 := false end
    else if xk then
    begin yv := c1 - xv; yk := true; r1 := false; changed := true end
    else if yk then
    begin xv := c1 - yv; xk := true; r1 := false; changed := true end
  end examine1;

  procedure examine2;
  comment the evaluator of R2, x - y = c2;
  begin
    x2 := x2 + 1;
    if xk ∧ yk then
    begin if xv - yv ≠ c2 then inconsistent := true; r2 := false end
    else if xk then
    begin yv := xv - c2; yk := true; r2 := false; changed := true end
    else if yk then
    begin xv := c2 + yv; xk := true; r2 := false; changed := true end
  end examine2;

  procedure propagate;
  comment every held relation is examined, in the order posed, again and again until a whole pass gives no unknown a value;
  begin
    changed := true;
    for pass := 1 while changed do
    begin
      changed := false;
      if r1 then examine1;
      if r2 then examine2
    end
  end propagate;

  procedure uname(u);
    value u; integer u;
  comment output adapter: the name of unknown u, 1 for x, 2 for y;
  if u = 1 then outstring(1, "x") else outstring(1, "y");

  procedure place(known, v, u);
    value known, v, u; Boolean known; integer v, u;
  comment output adapter: a place of a relation, its value if known, else the name of its unknown;
  if known then outinteger(1, v) else uname(u);

  procedure state(known, v, inheld, u);
    value known, v, inheld, u; Boolean known, inheld; integer v, u;
  comment output adapter: an unknown, as its value, or held by a relation, or free;
  begin
    uname(u);
    if known then begin outstring(1, " = "); outinteger(1, v) end
    else if inheld then outstring(1, " held")
    else outstring(1, " free")
  end state;

  procedure relations;
  comment output adapter: the relations held, separated by commas, with the values known put in their places;
  begin
    if r1 then
    begin place(xk, xv, 1); outstring(1, " + "); place(yk, yv, 2); outstring(1, " = "); outinteger(1, c1) end;
    if r2 then
    begin
      if r1 then outstring(1, ", ");
      place(xk, xv, 1); outstring(1, " - "); place(yk, yv, 2); outstring(1, " = "); outinteger(1, c2)
    end
  end relations;

  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constants;
  ininteger(0, c1); ininteger(0, c2);
  xk := yk := inconsistent := false;
  x1 := x2 := 0;
  r1 := r2 := true;

  propagate;

  comment the answer: every unknown, and the relations still held;
  if ¬inconsistent then
  begin
    outstring(1, "[answer]");
    state(xk, xv, r1 ∨ r2, 1); outstring(1, ", ");
    state(yk, yv, r1 ∨ r2, 2);
    if r1 ∨ r2 then begin outstring(1, ", where "); relations end;
    outstring(1, "[/answer]\n")
  end;

  comment observe: the relations held, the values known, how many relations wait, and how often each was examined;
  held := (if r1 then 1 else 0) + (if r2 then 1 else 0);
  outstring(1, "[observe]");
  if inconsistent then outstring(1, "no solution\n");
  outstring(1, "held relations: ");
  if held = 0 then outstring(1, "none") else relations;
  outstring(1, "\n");
  if xk then begin outstring(1, "[bind x]"); outinteger(1, xv); outstring(1, "[/bind]\n") end;
  if yk then begin outstring(1, "[bind y]"); outinteger(1, yv); outstring(1, "[/bind]\n") end;
  if held > 0 then
  begin outstring(1, "[suspended held-relations "); outinteger(1, held); outstring(1, "]\n") end;
  outstring(1, "[operations R1-examined "); outinteger(1, x1); outstring(1, "]\n");
  outstring(1, "[operations R2-examined "); outinteger(1, x2); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
end
