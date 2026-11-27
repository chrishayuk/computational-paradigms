begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: harness-algol-60 (the harness README's example, for the made-up problem X01, not a result);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report (1962), and the input and output procedures of the interpreter (IFIP 1964, Modified Report 1976);
  comment X01 (made up). One unknown integer x. Stage 1: x >= c1. Stage 2: x <= c2. Stage 3: x differs from c3. Query: every x. Constants file: a line 1: c1, a line 2: c2, a line 3: c3, each read when its stage is posed, three integers;
  integer n, cap, m, i, code, k, c1, c2, c3, lo, hi, ex, x, tested, held;
  Boolean haslo, hashi, hasex;

  comment harness words: the instance parameters, then the constants;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  haslo := hashi := hasex := false; tested := 0;

  for i := 1 while true do
  begin
    comment harness words: one message, the stage to pose;
    ininteger(0, code); ininteger(0, k);
    if k = 1 then begin ininteger(0, c1); lo := c1; haslo := true end
    else if k = 2 then begin ininteger(0, c2); hi := c2; hashi := true end
    else if k = 3 then begin ininteger(0, c3); ex := c3; hasex := true end;

    comment the query: every x, when the relations bound it on both sides;
    if haslo and hashi then
      for x := lo step 1 until hi do
      begin
        tested := tested + 1;
        if not (hasex and x = ex) then
        begin outstring(1, "[answer]x = "); outinteger(1, x); outstring(1, "[/answer]\n") end
      end;

    comment observe: the relations held, and how many wait for more information;
    held := (if haslo then 1 else 0) + (if hashi then 1 else 0) + (if hasex then 1 else 0);
    outstring(1, "[observe]");
    if haslo then begin outstring(1, "x >= "); outinteger(1, lo) end;
    if hashi then begin outstring(1, "x <= "); outinteger(1, hi) end;
    if hasex then begin outstring(1, "x <> "); outinteger(1, ex) end;
    if not (haslo and hashi) then
    begin outstring(1, "[suspended held-relations "); outinteger(1, held); outstring(1, "]") end;
    outstring(1, "[operations x-tested "); outinteger(1, tested); outstring(1, "]");
    outstring(1, "[/observe]\n[end]")
  end
end
