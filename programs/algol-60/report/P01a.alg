begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks, procedures with value and name parameters (4.7, 5.4), the for statement with a while element (4.6) and conditional statements and expressions (3.3, 4.5), the name parameters letting one evaluator of an equation serve both equations (4.7.3.2), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), the message loop and observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of each relation until its places are known, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS stages 1 and 2 have none. A line 3: k, the integer value of z in the equation z = k of stage 3;
  comment P01a. Unknowns x, y, z. Stage 1: x = y. Stage 2: y = z. Stage 3: z = k. ALGOL 60 has no unknowns, so each unknown is a Boolean that says whether it has a value and an integer that holds it, and each equation is held as posed until a place is known, when it gives the other place its value or is tested. The only value any stage gives is an integer, so the integer holds every value an unknown can take here;
  integer n, cap, m, i, code, k, c3, xv, yv, zv, held, pass;
  Boolean xk, yk, zk, r1, r2, r3, changed, inconsistent;

  procedure equation(ak, av, bk, bv, r);
    Boolean ak, bk, r; integer av, bv;
  comment the evaluator of an equation a = b, between two unknowns given by name: with both places known it is tested, with one known it gives the other its value, and with neither it waits. r is the equation, true while it is held;
  begin
    if ak and bk then
    begin if not (av = bv) then inconsistent := true; r := false end
    else if ak then
    begin bv := av; bk := true; r := false; changed := true end
    else if bk then
    begin av := bv; ak := true; r := false; changed := true end
  end equation;

  procedure value3;
  comment the evaluator of the equation z = k of stage 3: z is tested if known, else given k;
  begin
    if zk then
    begin if not (zv = c3) then inconsistent := true end
    else
    begin zv := c3; zk := true; changed := true end;
    r3 := false
  end value3;

  procedure propagate;
  comment every held equation is examined, in the order posed, again and again until a whole pass gives no unknown a value;
  begin
    changed := true;
    for pass := 1 while changed do
    begin
      changed := false;
      if r1 then equation(xk, xv, yk, yv, r1);
      if r2 then equation(yk, yv, zk, zv, r2);
      if r3 then value3
    end
  end propagate;

  procedure uname(u);
    value u; integer u;
  comment output adapter: the name of unknown u, 1 for x, 2 for y, 3 for z;
  if u = 1 then outstring(1, "x") else if u = 2 then outstring(1, "y") else outstring(1, "z");

  procedure place(known, v, u);
    value known, v, u; Boolean known; integer v, u;
  comment output adapter: a place of an equation, its value if known, else the name of its unknown;
  if known then outinteger(1, v) else uname(u);

  procedure state(known, v, inheld, u);
    value known, v, inheld, u; Boolean known, inheld; integer v, u;
  comment output adapter: an unknown, as its value, or held by an equation, or free;
  begin
    uname(u);
    if known then begin outstring(1, " = "); outinteger(1, v) end
    else if inheld then outstring(1, " held")
    else outstring(1, " free")
  end state;

  procedure relations;
  comment output adapter: the equations held, separated by commas;
  begin
    if r1 then begin place(xk, xv, 1); outstring(1, " = "); place(yk, yv, 2) end;
    if r1 and r2 then outstring(1, ", ");
    if r2 then begin place(yk, yv, 2); outstring(1, " = "); place(zk, zv, 3) end
  end relations;

  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  xk := yk := zk := r1 := r2 := r3 := inconsistent := false;

  for i := 1 while true do
  begin
    comment harness words: one message, the stage it poses, and then that stage's constants;
    ininteger(0, code); ininteger(0, k);
    if k = 1 then r1 := true
    else if k = 2 then r2 := true
    else if k = 3 then begin ininteger(0, c3); r3 := true end;

    propagate;

    comment the answer: every unknown, and the equations still held;
    if not inconsistent then
    begin
      outstring(1, "[answer]");
      state(xk, xv, r1, 1); outstring(1, ", ");
      state(yk, yv, r1 or r2, 2); outstring(1, ", ");
      state(zk, zv, r2 or r3, 3);
      if r1 or r2 then begin outstring(1, ", where "); relations end;
      outstring(1, "[/answer]\n")
    end;

    comment observe: the equations held, the values known, and how many equations wait;
    held := (if r1 then 1 else 0) + (if r2 then 1 else 0) + (if r3 then 1 else 0);
    outstring(1, "[observe]");
    if inconsistent then outstring(1, "no solution\n");
    outstring(1, "held equations: ");
    if held = 0 then outstring(1, "none") else relations;
    outstring(1, "\n");
    if xk then begin outstring(1, "[bind x]"); outinteger(1, xv); outstring(1, "[/bind]\n") end;
    if yk then begin outstring(1, "[bind y]"); outinteger(1, yv); outstring(1, "[/bind]\n") end;
    if zk then begin outstring(1, "[bind z]"); outinteger(1, zv); outstring(1, "[/bind]\n") end;
    if held > 0 then
    begin outstring(1, "[suspended held-relations "); outinteger(1, held); outstring(1, "]\n") end;
    outstring(1, "[/observe]\n[end]")
  end
end
