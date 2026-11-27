begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: harness-algol-60 (qualification program for a made-up problem, not a result);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report (1962), and the interpreter's input and output procedures;
  comment X05 (made up). Stage 1: x = c1. Stage 2: a[x] = c2, where a has bounds 1 and 2. Stage 3: x = x + c3. Constants file: lines 1: c1, 2: c2, 3: c3;
  integer n, cap, m, i, code, k, c1, c2, c3, x;
  integer array a[1:2];
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  for i := 1 while true do
  begin
    ininteger(0, code); ininteger(0, k);
    if k = 1 then begin ininteger(0, c1); x := c1 end
    else if k = 2 then begin ininteger(0, c2); a[x] := c2 end
    else if k = 3 then begin ininteger(0, c3); x := x + c3 end;
    outstring(1, "[answer]x = "); outinteger(1, x); outstring(1, "[/answer]\n[end]")
  end
end
