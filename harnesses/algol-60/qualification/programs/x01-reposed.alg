begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: harness-algol-60 (qualification program for the made-up problem X01, not a result);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: as x01-incremental.alg;
  comment X01 (made up), posed by rerunning with stages 1 to k: the program reads its replayed stages and the posed stage, and then computes the query once. Constants file: a line 1: c1, a line 2: c2, a line 3: c3, each read when its stage is posed;
  integer n, cap, m, i, code, k, c1, c2, c3, lo, hi, ex, x, tested, held;
  Boolean haslo, hashi, hasex, posed;

  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  haslo := hashi := hasex := posed := false; tested := 0;

  for i := 1 while not posed do
  begin
    ininteger(0, code); ininteger(0, k);
    posed := code = 1;
    if k = 1 then begin ininteger(0, c1); lo := c1; haslo := true end
    else if k = 2 then begin ininteger(0, c2); hi := c2; hashi := true end
    else if k = 3 then begin ininteger(0, c3); ex := c3; hasex := true end;
    if not posed then outstring(1, "[end]")
  end;

  if haslo and hashi then
    for x := lo step 1 until hi do
    begin
      tested := tested + 1;
      if not (hasex and x = ex) then
      begin outstring(1, "[answer]x = "); outinteger(1, x); outstring(1, "[/answer]\n") end
    end;
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
