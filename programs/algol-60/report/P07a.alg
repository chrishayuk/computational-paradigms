begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays (5.2), procedures (5.4), the for statement with step-until and while elements (4.6), conditional statements and expressions (3.3, 4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of each relation until enough of its places are known, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS a line 1: c1 c2 c3, the integers of R1, x + y + z = c1, R2, y + z = c2, and R3, z = c3, in the order the problem writes the relations, whatever the instance's order;
  comment P07a, every instance. Integer unknowns x, y, z. One stage: R1, R2 and R3, posed in the instance's order, which the instance line gives as the codes of the relations by their place as written. Each unknown is a Boolean that says whether it has a value and an integer that holds it. Each relation is held as posed until enough of its places are known, when it gives the remaining place its value or is tested. Every held relation is examined in the order posed, again and again, until a whole pass gives no unknown a value;
  integer n, cap, m, i, code, k, c1, c2, c3, xv, yv, zv, held, pass, x1, x2, x3;
  Boolean xk, yk, zk, r1, r2, r3, changed, inconsistent;
  integer array ord[1:3];

  procedure examine1;
  comment the evaluator of R1, x + y + z = c1: with two places known it gives the third its value, with all three known it is tested;
  begin
    x1 := x1 + 1;
    if xk ∧ yk ∧ zk then
    begin if xv + yv + zv ≠ c1 then inconsistent := true; r1 := false end
    else if yk ∧ zk then
    begin xv := c1 - yv - zv; xk := true; r1 := false; changed := true end
    else if xk ∧ zk then
    begin yv := c1 - xv - zv; yk := true; r1 := false; changed := true end
    else if xk ∧ yk then
    begin zv := c1 - xv - yv; zk := true; r1 := false; changed := true end
  end examine1;

  procedure examine2;
  comment the evaluator of R2, y + z = c2;
  begin
    x2 := x2 + 1;
    if yk ∧ zk then
    begin if yv + zv ≠ c2 then inconsistent := true; r2 := false end
    else if yk then
    begin zv := c2 - yv; zk := true; r2 := false; changed := true end
    else if zk then
    begin yv := c2 - zv; yk := true; r2 := false; changed := true end
  end examine2;

  procedure examine3;
  comment the evaluator of R3, z = c3;
  begin
    x3 := x3 + 1;
    if zk then
    begin if zv ≠ c3 then inconsistent := true end
    else
    begin zv := c3; zk := true; changed := true end;
    r3 := false
  end examine3;

  procedure propagate;
  comment every held relation is examined, in the order posed, again and again until a whole pass gives no unknown a value;
  begin
    integer j;
    changed := true;
    for pass := 1 while changed do
    begin
      changed := false;
      for j := 1 step 1 until 3 do
      begin
        if ord[j] = 1 then begin if r1 then examine1 end
        else if ord[j] = 2 then begin if r2 then examine2 end
        else if ord[j] = 3 then begin if r3 then examine3 end
      end
    end
  end propagate;

  procedure uname(u);
    value u; integer u;
  comment output adapter: the name of unknown u, 1 for x, 2 for y, 3 for z;
  if u = 1 then outstring(1, "x") else if u = 2 then outstring(1, "y") else outstring(1, "z");

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
  comment output adapter: the relations held, in the order posed, separated by commas, with the values known put in their places;
  begin
    integer j;
    Boolean first;
    first := true;
    for j := 1 step 1 until 3 do
    begin
      if ord[j] = 1 ∧ r1 then
      begin
        if ¬first then outstring(1, ", ");
        place(xk, xv, 1); outstring(1, " + "); place(yk, yv, 2); outstring(1, " + "); place(zk, zv, 3);
        outstring(1, " = "); outinteger(1, c1); first := false
      end
      else if ord[j] = 2 ∧ r2 then
      begin
        if ¬first then outstring(1, ", ");
        place(yk, yv, 2); outstring(1, " + "); place(zk, zv, 3); outstring(1, " = "); outinteger(1, c2); first := false
      end
      else if ord[j] = 3 ∧ r3 then
      begin
        if ¬first then outstring(1, ", ");
        place(zk, zv, 3); outstring(1, " = "); outinteger(1, c3); first := false
      end
    end
  end relations;

  comment harness words: the instance line, whose codes are the instance's order, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, ord[i]);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constants;
  ininteger(0, c1); ininteger(0, c2); ininteger(0, c3);
  xk := yk := zk := inconsistent := false;
  x1 := x2 := x3 := 0;
  r1 := r2 := r3 := true;

  propagate;

  comment the answer: every unknown, and the relations still held;
  if ¬inconsistent then
  begin
    outstring(1, "[answer]");
    state(xk, xv, r1, 1); outstring(1, ", ");
    state(yk, yv, r1 ∨ r2, 2); outstring(1, ", ");
    state(zk, zv, r1 ∨ r2 ∨ r3, 3);
    if r1 ∨ r2 ∨ r3 then begin outstring(1, ", where "); relations end;
    outstring(1, "[/answer]\n")
  end;

  comment observe: the relations held, the values known, how many relations wait, and how often each was examined;
  held := (if r1 then 1 else 0) + (if r2 then 1 else 0) + (if r3 then 1 else 0);
  outstring(1, "[observe]");
  if inconsistent then outstring(1, "no solution\n");
  outstring(1, "held relations: ");
  if held = 0 then outstring(1, "none") else relations;
  outstring(1, "\n");
  if xk then begin outstring(1, "[bind x]"); outinteger(1, xv); outstring(1, "[/bind]\n") end;
  if yk then begin outstring(1, "[bind y]"); outinteger(1, yv); outstring(1, "[/bind]\n") end;
  if zk then begin outstring(1, "[bind z]"); outinteger(1, zv); outstring(1, "[/bind]\n") end;
  if held > 0 then
  begin outstring(1, "[suspended held-relations "); outinteger(1, held); outstring(1, "]\n") end;
  outstring(1, "[operations R1-examined "); outinteger(1, x1); outstring(1, "]\n");
  outstring(1, "[operations R2-examined "); outinteger(1, x2); outstring(1, "]\n");
  outstring(1, "[operations R3-examined "); outinteger(1, x3); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
end
