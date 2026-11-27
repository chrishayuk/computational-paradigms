begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays (5.2), procedures (5.4), the for statement (4.6), conditional statements and expressions (3.3, 4.5), and the standard functions sqrt and entier (3.2.4, 3.2.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8), and the holding of a relation until enough of its places are known, written for this problem (METRICS.md, rule 19), with no period source;
  comment CONSTANTS a line 1: c, the integer of R1, x times x = c;
  comment P07g. One integer unknown x. One stage: R1, x times x = c. x has no value, or the values held in the array xs, all at once. R1 is held as posed until a place is known. Its one unknown is x, in both its places, and c is known, so it gives x its values: the integers whose square is c, the root r of c by sqrt, rounded, if r times r = c, and its negation, or none if no integer square is c;
  integer n, cap, m, i, code, k, c1, r, nx, held, x1;
  Boolean r1, inconsistent;
  integer array xs[1:2];

  procedure examine1;
  comment the evaluator of R1, x times x = c1. With x known, each of its values is tested. With x unknown, x is given every integer whose square is c1;
  begin
    integer j, kept;
    x1 := x1 + 1;
    if nx > 0 then
    begin
      kept := 0;
      for j := 1 step 1 until nx do
      begin if xs[j] × xs[j] = c1 then begin kept := kept + 1; xs[kept] := xs[j] end end;
      nx := kept;
      if nx = 0 then inconsistent := true
    end
    else if c1 < 0 then inconsistent := true
    else
    begin
      r := entier(sqrt(c1) + 0.5);
      if r × r ≠ c1 then inconsistent := true
      else if r = 0 then begin nx := 1; xs[1] := 0 end
      else begin nx := 2; xs[1] := r; xs[2] := -r end
    end;
    r1 := false
  end examine1;

  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constant;
  ininteger(0, c1);
  inconsistent := false; nx := 0; x1 := 0;
  r1 := true;

  if r1 then examine1;

  comment the answers: each value of x;
  if ¬inconsistent then
  begin
    for i := 1 step 1 until nx do
    begin outstring(1, "[answer]x = "); outinteger(1, xs[i]); outstring(1, "[/answer]\n") end
  end;

  comment observe: the relation held, the values of x held, and how often the relation was examined;
  held := if r1 then 1 else 0;
  outstring(1, "[observe]");
  if inconsistent then outstring(1, "no solution\n");
  outstring(1, "held relations: none\n");
  if ¬inconsistent then
  begin
    outstring(1, "values of x held, all at once:");
    for i := 1 step 1 until nx do begin outstring(1, " "); outinteger(1, xs[i]) end;
    outstring(1, "\n")
  end;
  outstring(1, "[operations R1-examined "); outinteger(1, x1); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
end
