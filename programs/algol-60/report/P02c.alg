begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks, procedures (5.4), the for statement with a while element (4.6), conditional statements and expressions (3.3, 4.5) and integer division (3.3.4.2), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of each relation until enough of its places are known, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS one line 1: c a b, where c is the right side of R1, u + v = c, and a and b are the two integers of R3, u + a = b. R2, w times u = v, has none;
  comment P02c. Integer unknowns u, v, w. One stage: R1, R2 and R3, in that order, posed by rerunning (there is no later stage to wait for). Each unknown is a Boolean that says whether it has a value and an integer that holds it. Each relation is held as posed until enough of its places are known, when it gives the remaining place its value or is tested;
  integer n, cap, m, i, code, k, c1, a3, b3, uv, vv, wv, held, pass, x1, x2, x3;
  Boolean uk, vk, wk, r1, r2, r3, changed, inconsistent;

  procedure examine1;
  comment the evaluator of R1, u + v = c1;
  begin
    x1 := x1 + 1;
    if uk and vk then
    begin if not (uv + vv = c1) then inconsistent := true; r1 := false end
    else if uk then
    begin vv := c1 - uv; vk := true; r1 := false; changed := true end
    else if vk then
    begin uv := c1 - vv; uk := true; r1 := false; changed := true end
  end examine1;

  procedure examine2;
  comment the evaluator of R2, w times u = v. With u known and nonzero, w is v divided by u where u divides v, and there is no solution where it does not. With u = 0, R2 holds for every w when v = 0, and for none when v is not 0. The same with w and u exchanged;
  begin
    x2 := x2 + 1;
    if uk and wk and vk then
    begin if not (wv × uv = vv) then inconsistent := true; r2 := false end
    else if uk and wk then
    begin vv := wv × uv; vk := true; r2 := false; changed := true end
    else if uk and vk then
    begin
      if uv = 0 then
      begin if not (vv = 0) then inconsistent := true end
      else if vv ÷ uv × uv = vv then
      begin wv := vv ÷ uv; wk := true; changed := true end
      else inconsistent := true;
      r2 := false
    end
    else if wk and vk then
    begin
      if wv = 0 then
      begin if not (vv = 0) then inconsistent := true end
      else if vv ÷ wv × wv = vv then
      begin uv := vv ÷ wv; uk := true; changed := true end
      else inconsistent := true;
      r2 := false
    end
  end examine2;

  procedure examine3;
  comment the evaluator of R3, u + a3 = b3;
  begin
    x3 := x3 + 1;
    if uk then
    begin if not (uv + a3 = b3) then inconsistent := true end
    else
    begin uv := b3 - a3; uk := true; changed := true end;
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
  comment output adapter: the name of unknown u, 1 for u, 2 for v, 3 for w;
  if u = 1 then outstring(1, "u") else if u = 2 then outstring(1, "v") else outstring(1, "w");

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
  comment output adapter: the relations held, separated by commas, with the values known put in their places;
  begin
    Boolean first;
    first := true;
    if r1 then
    begin place(uk, uv, 1); outstring(1, " + "); place(vk, vv, 2); outstring(1, " = "); outinteger(1, c1); first := false end;
    if r2 then
    begin
      if not first then outstring(1, ", ");
      place(wk, wv, 3); outstring(1, " . "); place(uk, uv, 1); outstring(1, " = "); place(vk, vv, 2); first := false
    end;
    if r3 then
    begin
      if not first then outstring(1, ", ");
      place(uk, uv, 1); outstring(1, " + "); outinteger(1, a3); outstring(1, " = "); outinteger(1, b3)
    end
  end relations;

  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  uk := vk := wk := r1 := r2 := r3 := inconsistent := false;
  x1 := x2 := x3 := 0;

  comment harness words: the one message, which poses stage 1, and then its constants;
  ininteger(0, code); ininteger(0, k);
  comment R1, R2 and R3, in that order, as one stage;
  ininteger(0, c1); r1 := true;
  r2 := true;
  ininteger(0, a3); ininteger(0, b3); r3 := true;

  propagate;

  comment the answer: every unknown, and the relations still held;
  if not inconsistent then
  begin
    outstring(1, "[answer]");
    state(uk, uv, r1 or r2 or r3, 1); outstring(1, ", ");
    state(vk, vv, r1 or r2, 2); outstring(1, ", ");
    state(wk, wv, r2, 3);
    if r1 or r2 or r3 then begin outstring(1, ", where "); relations end;
    outstring(1, "[/answer]\n")
  end;

  comment observe: the relations held, the values known, how many relations wait, and how often each was examined;
  held := (if r1 then 1 else 0) + (if r2 then 1 else 0) + (if r3 then 1 else 0);
  outstring(1, "[observe]");
  if inconsistent then outstring(1, "no solution\n");
  outstring(1, "held relations: ");
  if held = 0 then outstring(1, "none") else relations;
  outstring(1, "\n");
  if uk then begin outstring(1, "[bind u]"); outinteger(1, uv); outstring(1, "[/bind]\n") end;
  if vk then begin outstring(1, "[bind v]"); outinteger(1, vv); outstring(1, "[/bind]\n") end;
  if wk then begin outstring(1, "[bind w]"); outinteger(1, wv); outstring(1, "[/bind]\n") end;
  if held > 0 then
  begin outstring(1, "[suspended held-relations "); outinteger(1, held); outstring(1, "]\n") end;
  outstring(1, "[operations R1-examined "); outinteger(1, x1); outstring(1, "]\n");
  outstring(1, "[operations R2-examined "); outinteger(1, x2); outstring(1, "]\n");
  outstring(1, "[operations R3-examined "); outinteger(1, x3); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
end
