begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for procedures with value and name parameters (4.7, 5.4) and procedures as actual parameters (4.7.5, 5.4.4), each solution being passed to a parameterless procedure in the way of the procedures passed as parameters in Knuth's man or boy test (1964, examples/man-or-boy-1964.alg in the image, cited after batch 1B's reading of it), a go to statement that leaves a procedure at once (4.3, examples/exits.alg in the image, cited after batch 1C's reading of it), the for statement (4.6) and conditional statements (4.5), the input and output procedures ininteger and outstring as the interpreter gives them (IFIP 1964, systems file), atoms as integer codes (systems file, Values), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: p q, the two requests of grant(p, q, g), each as the code of its atom, A being 1 and B being 2;
  comment P15c. grant(p, q, g), any one, by its two facts in order, as a procedure that passes each solution g to the parameterless procedure found. Fact 1: grant(p, q, p). Fact 2: grant(p, q, q). The query asks for any one answer: found reports the first solution, g = p, and leaves the procedure at once by a go to statement, so fact 2 is never tried, and nothing is kept that could revisit the choice. The choice is made by the order of the facts;
  integer n, cap, m, i, code, k, p, q, g, nsol, gr1, gr2;

  procedure grant(p, q, g, found);
    value p, q; integer p, q, g; procedure found;
  comment grant(p, q, g), g unknown, by its facts in order, each solution passed to found;
  begin
    comment fact 1: grant(p, q, p);
    gr1 := gr1 + 1;
    g := p;
    found;
    comment fact 2: grant(p, q, q);
    gr2 := gr2 + 1;
    g := q;
    found
  end grant;

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

  procedure found;
  comment the first solution g is reported, and the query is left there;
  begin
    nsol := nsol + 1;
    outstring(1, "[answer]g = "); num(g); outstring(1, "[/answer]\n");
    go to done
  end found;

  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  nsol := gr1 := gr2 := 0;
  comment the stage's constants: the two requests;
  ininteger(0, p); ininteger(0, q);

  comment the query: grant(p, q, g), any one;
  grant(p, q, g, found);

  comment observe: which fact gave the grant, and what is kept. The query comes here by the go to statement in found;
done:
  outstring(1, "[observe]");
  if nsol = 0 then outstring(1, "no solution\n");
  outstring(1, "atoms as codes: A is 1, B is 2\n");
  outstring(1, "committed: the grant was given by the first fact, the second was never tried, and nothing is kept to try it\n");
  outstring(1, "[bind g]"); num(g); outstring(1, "[/bind]\n");
  outstring(1, "[operations grant/1 "); num(gr1); outstring(1, "]\n");
  outstring(1, "[operations grant/2 "); num(gr2); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
end
