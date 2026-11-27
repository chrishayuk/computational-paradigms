begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: harness-algol-60 (qualification program for a made-up problem, not a result);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report (1962), and the interpreter's input and output procedures;
  comment X03 (made up). One stage spawns two computations: U, u = 1 + 2 + ... + n, and V, v = n times n. The instance gives n and the spawn order. No constants;
  integer n, cap, m, i, code, k, c, s, j;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  for i := 1 while true do
  begin
    ininteger(0, code); ininteger(0, k); ininteger(0, c);
    if c = 1 then
    begin s := 0; for j := 1 step 1 until n do s := s + j;
      outstring(1, "[answer]u = "); outinteger(1, s); outstring(1, "[/answer]") end
    else if c = 2 then
    begin outstring(1, "[answer]v = "); outinteger(1, n × n); outstring(1, "[/answer]") end;
    outstring(1, "\n[end]")
  end
end
