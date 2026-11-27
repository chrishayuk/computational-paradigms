begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: harness-algol-60 (qualification program for a made-up problem, not a result);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report (1962), and the interpreter's input and output procedures;
  comment X07 (made up). One stage, which reads input it is never given. No constants;
  integer n, cap, m, i, code, k, extra;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  outstring(1, "[answer]n = "); outinteger(1, n); outstring(1, "[/answer]");
  for i := 1 while true do ininteger(0, extra)
end
