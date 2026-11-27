begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: harness-algol-60 (qualification program for a made-up problem, not a result);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report (1962), and the interpreter's input and output procedures;
  comment X02 (made up). Stage 1: choose p in 1..c1, the least, and emit it. Stage 2: commit to p and emit the commitment. Stage 3: p differs from c3. Constants file: a line 1: c1 and a line 3: c3. An answer is p alone, so that a replayed commitment v can be read back with ininteger;
  integer n, cap, m, i, code, k, c1, c3, p;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  p := 0; code := 0;
  for i := 1 while code ≠ 1 do
  begin
    ininteger(0, code); ininteger(0, k);
    if code = 3 then ininteger(0, p)
    else if k = 1 then
    begin ininteger(0, c1); if c1 >= 1 then p := 1; outstring(1, "[emit]chose "); outinteger(1, p); outstring(1, "[/emit]") end
    else if k = 2 then
    begin outstring(1, "[emit]commit "); outinteger(1, p); outstring(1, "[/emit]") end
    else if k = 3 then
    begin ininteger(0, c3); if p = c3 then p := 0 end;
    if code = 1 ∧ p > 0 then begin outstring(1, "[answer]"); outinteger(1, p); outstring(1, "[/answer]") end;
    if code ≠ 1 then outstring(1, "\n[end]")
  end;
  outstring(1, "\n[observe][bind p]"); outinteger(1, p); outstring(1, "[/bind][/observe]\n[end]")
end
