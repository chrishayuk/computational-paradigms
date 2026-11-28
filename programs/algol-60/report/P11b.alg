begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays (5.2), procedures (5.4), the for statement with step-until and while elements (4.6) and conditional statements (4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), the effect stub emit bound as printing (harnesses/algol-60/README.md, 2.5), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: F f1 ... fF c, the number of facts of pick, the value of each fact, in order, and then c, the integer of x at least c;
  comment P11b. One stage, a query for any one outcome: pick(x) and emit(x) and x at least c, in that order. pick is given by its facts: each fact, in order, gives x a value, and the conjuncts after pick are carried out on it in order. The query asks for one answer, so the facts are tried only until one passes the whole conjunction. An answer, and the entry emitted, is x alone, its digits printed with no spaces;
  integer n, cap, m, i, code, k, j, nf, c, xv, cur;
  Boolean ok;
  integer array fv[1:1000], pk[1:1000];

  procedure num(v);
    value v; integer v;
  comment output adapter: an integer, a minus sign if it is negative and then its decimal digits, with no spaces;
  begin
    integer d;
    if v < 0 then begin outstring(1, "-"); num(-v) end
    else
    begin
      if v ≥ 10 then num(v ÷ 10);
      d := v - v ÷ 10 × 10;
      if d = 0 then outstring(1, "0") else if d = 1 then outstring(1, "1") else if d = 2 then outstring(1, "2")
      else if d = 3 then outstring(1, "3") else if d = 4 then outstring(1, "4") else if d = 5 then outstring(1, "5")
      else if d = 6 then outstring(1, "6") else if d = 7 then outstring(1, "7") else if d = 8 then outstring(1, "8")
      else outstring(1, "9")
    end
  end num;

  procedure emit(v);
    value v; integer v;
  comment the effect stub emit(v) of the harness, bound as printing;
  begin outstring(1, "[emit]"); num(v); outstring(1, "[/emit]\n") end emit;

  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constants: pick's facts, and c;
  ininteger(0, nf);
  for j := 1 step 1 until nf do begin ininteger(0, fv[j]); pk[j] := 0 end;
  ininteger(0, c);

  comment the query: pick(x) and emit(x) and x at least c, in that order, until one x passes;
  ok := false; cur := 0;
  for j := 0 while ¬ok ∧ cur < nf do
  begin
    cur := cur + 1; pk[cur] := pk[cur] + 1;
    xv := fv[cur];
    emit(xv);
    if xv ≥ c then ok := true
  end;

  if ok then begin outstring(1, "[answer]"); num(xv); outstring(1, "[/answer]\n") end;

  comment observe: the value of x, and the facts of pick tried;
  outstring(1, "[observe]");
  if ¬ok then outstring(1, "no solution\n");
  if ok then begin outstring(1, "[bind x]"); num(xv); outstring(1, "[/bind]\n") end;
  outstring(1, "facts of pick tried: "); num(cur); outstring(1, " of "); num(nf); outstring(1, "\n");
  for j := 1 step 1 until nf do
  begin outstring(1, "[operations pick/"); num(j); outstring(1, " "); outinteger(1, pk[j]); outstring(1, "]\n") end;
  outstring(1, "[/observe]\n[end]")
end
