begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for assignment statements (4.2), the for statement with a while element (4.6) and conditional statements (4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), and the message loop and observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: e, of b becomes e. A line 2: f, of d becomes f . b. A line 3: e, of b becomes b + e. A line 4: e, of b becomes e;
  comment P10c. Named quantities b and d, each an integer variable with a Boolean that says whether it has a value. Each stage replaces a value by an assignment, the right side taken at the values before the stage. d becomes f . b is an assignment, computed once, and d keeps that value when b is replaced. Earlier values are not kept;
  integer n, cap, m, i, code, k, e, f, b, d;
  Boolean bk, dk;

  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  bk := dk := false;

  for i := 1 while true do
  begin
    comment harness words: one message, the stage it poses, and then that stage's constants;
    ininteger(0, code); ininteger(0, k);
    if k = 1 then
    begin comment b becomes e;
      ininteger(0, e); b := e; bk := true end
    else if k = 2 then
    begin comment d becomes f . b;
      ininteger(0, f); d := f × b; dk := true end
    else if k = 3 then
    begin comment b becomes b + e;
      ininteger(0, e); b := b + e end
    else if k = 4 then
    begin comment b becomes e;
      ininteger(0, e); b := e end;

    comment the answer: the values b and d have now;
    outstring(1, "[answer]b");
    if bk then begin outstring(1, " = "); outinteger(1, b) end else outstring(1, " has no value");
    outstring(1, ", d");
    if dk then begin outstring(1, " = "); outinteger(1, d) end else outstring(1, " has no value");
    outstring(1, "[/answer]\n");

    comment observe: the one value held for each quantity;
    outstring(1, "[observe]");
    outstring(1, "b and d are variables, replaced by assignment, and their earlier values are not kept. No relation is held\n");
    if bk then begin outstring(1, "[bind b]"); outinteger(1, b); outstring(1, "[/bind]\n") end;
    if dk then begin outstring(1, "[bind d]"); outinteger(1, d); outstring(1, "[/bind]\n") end;
    outstring(1, "[/observe]\n[end]")
  end
end
