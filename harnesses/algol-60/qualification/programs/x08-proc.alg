begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: harness-algol-60 (qualification program for a made-up problem, not a result);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report (1962), and the interpreter's input and output procedures;
  comment X08 (made up), a step probe of systems/algol-60/README.md, Units: a procedure statement whose body is one assignment: 3 steps more than base. No constants;
  integer n, cap, m, i, j, code, k;
  procedure q; j := 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  j := 0;
  j := j; q;
  outstring(1, "[answer]j = "); outinteger(1, j); outstring(1, "[/answer]\n[end]");
  ininteger(0, code)
end
