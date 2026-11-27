begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks, procedures (5.4), the for statement with a while element (4.6), conditional statements and expressions (3.3, 4.5) and integer division (3.3.4.2), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of each relation until enough of its places are known, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS a line 1: c2 c3, the integers of R2, u = c2, and R3, v = c3;
  comment P07d, and P07e, which has the same stage with other constants. Integer unknowns w, u, v. One stage: R1, w times u = v, then R2, then R3. Each unknown is a Boolean that says whether it has a value and an integer that holds it. Each relation is held as posed until enough of its places are known, when it gives the remaining place its value or is tested. Every held relation is examined in the order posed, again and again, until a whole pass gives no unknown a value;
  integer n, cap, m, i, code, k, c2, c3, wv, uv, vv, held, pass, x1, x2, x3;
  Boolean wk, uk, vk, r1, r2, r3, changed, inconsistent;

  procedure examine1;
  comment the evaluator of R1, w times u = v. With u known and not 0, w is v divided by u where u divides v, and there is no integer solution where it does not. With u = 0, R1 holds for every w when v = 0, and for none when v is not 0. The same with w and u exchanged;
  begin
    x1 := x1 + 1;
    if uk ∧ wk ∧ vk then
    begin if wv × uv ≠ vv then inconsistent := true; r1 := false end
    else if uk ∧ wk then
    begin vv := wv × uv; vk := true; r1 := false; changed := true end
    else if uk ∧ vk then
    begin
      if uv = 0 then
      begin if vv ≠ 0 then inconsistent := true end
      else if vv ÷ uv × uv = vv then
      begin wv := vv ÷ uv; wk := true; changed := true end
      else inconsistent := true;
      r1 := false
    end
    else if wk ∧ vk then
    begin
      if wv = 0 then
      begin if vv ≠ 0 then inconsistent := true end
      else if vv ÷ wv × wv = vv then
      begin uv := vv ÷ wv; uk := true; changed := true end
      else inconsistent := true;
      r1 := false
    end
  end examine1;

  procedure examine2;
  comment the evaluator of R2, u = c2;
  begin
    x2 := x2 + 1;
    if uk then
    begin if uv ≠ c2 then inconsistent := true end
    else
    begin uv := c2; uk := true; changed := true end;
    r2 := false
  end examine2;

  procedure examine3;
  comment the evaluator of R3, v = c3;
  begin
    x3 := x3 + 1;
    if vk then
    begin if vv ≠ c3 then inconsistent := true end
    else
    begin vv := c3; vk := true; changed := true end;
    r3 := false
  end examine3;

  procedure propagate;
  comment every held relation is examined, in the order R1, R2, R3, again and again until a whole pass gives no unknown a value;
  begin
    changed := true;
    for pass := 1 while changed do
    begin
      changed := false;
      if r1 then examine1;
      if r2 then examine2;
      if r3 then examine3
    end
  end propagate;

  procedure uname(u);
    value u; integer u;
  comment output adapter: the name of unknown u, 1 for w, 2 for u, 3 for v;
  if u = 1 then outstring(1, "w") else if u = 2 then outstring(1, "u") else outstring(1, "v");

  procedure place(known, x, u);
    value known, x, u; Boolean known; integer x, u;
  comment output adapter: a place of a relation, its value if known, else the name of its unknown;
  if known then outinteger(1, x) else uname(u);

  procedure state(known, x, inheld, u);
    value known, x, inheld, u; Boolean known, inheld; integer x, u;
  comment output adapter: an unknown, as its value, or held by a relation, or free;
  begin
    uname(u);
    if known then begin outstring(1, " = "); outinteger(1, x) end
    else if inheld then outstring(1, " held")
    else outstring(1, " free")
  end state;

  procedure relations;
  comment output adapter: the relations held, separated by commas, with the values known put in their places. The product is printed as a full stop;
  begin
    Boolean first;
    first := true;
    if r1 then
    begin place(wk, wv, 1); outstring(1, " . "); place(uk, uv, 2); outstring(1, " = "); place(vk, vv, 3); first := false end;
    if r2 then
    begin
      if ¬first then outstring(1, ", ");
      place(uk, uv, 2); outstring(1, " = "); outinteger(1, c2); first := false
    end;
    if r3 then
    begin
      if ¬first then outstring(1, ", ");
      place(vk, vv, 3); outstring(1, " = "); outinteger(1, c3)
    end
  end relations;

  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constants;
  ininteger(0, c2); ininteger(0, c3);
  wk := uk := vk := inconsistent := false;
  x1 := x2 := x3 := 0;
  r1 := r2 := r3 := true;

  propagate;

  comment the answer: every unknown, and the relations still held;
  if ¬inconsistent then
  begin
    outstring(1, "[answer]");
    state(wk, wv, r1, 1); outstring(1, ", ");
    state(uk, uv, r1 ∨ r2, 2); outstring(1, ", ");
    state(vk, vv, r1 ∨ r3, 3);
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
  if wk then begin outstring(1, "[bind w]"); outinteger(1, wv); outstring(1, "[/bind]\n") end;
  if uk then begin outstring(1, "[bind u]"); outinteger(1, uv); outstring(1, "[/bind]\n") end;
  if vk then begin outstring(1, "[bind v]"); outinteger(1, vv); outstring(1, "[/bind]\n") end;
  if held > 0 then
  begin outstring(1, "[suspended held-relations "); outinteger(1, held); outstring(1, "]\n") end;
  outstring(1, "[operations R1-examined "); outinteger(1, x1); outstring(1, "]\n");
  outstring(1, "[operations R2-examined "); outinteger(1, x2); outstring(1, "]\n");
  outstring(1, "[operations R3-examined "); outinteger(1, x3); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
end
