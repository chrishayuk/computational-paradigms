begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for procedures with value and name parameters (4.7, 5.4) and procedures as actual parameters (4.7.5, 5.4.4), each solution being passed to a parameterless procedure in the way of the procedures passed as parameters in Knuth's man or boy test (1964, examples/man-or-boy-1964.alg in the image), the for statement (4.6) and conditional statements (4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), and the message loop, spawn message and observe block of the harness README (harnesses/algol-60/README.md, 2.2, 2.6 and the example X01 of 2.8);
  comment CONSTANTS a line 1: c1 c2 c3, the integers of computation A, x = c1 and x = c2, and of computation B, y = c3. The harness sends the line after each spawn message of stage 1, and each computation reads all of it;
  comment P09b. Two computations, spawned one after the other by the harness, in the instance's spawn order. A: x = c1 and x = c2, its conjuncts in that order. B: y = c3. Each equation is a procedure that passes its solution, if any, to the procedure found: with its unknown known it is tested, else the unknown is given the value for as long as found runs. ALGOL 60 has one computation only, so a spawned computation is a procedure of this program, run to its end before the next message is read. Both share the variables of the outer block, and A and B have no unknown in common;
  integer n, cap, m, i, code, k, c, c1, c2, c3, xv, yv, na, nb;
  Boolean xk, yk;

  procedure equals(uk, u, cv, found);
    value cv; Boolean uk; integer u, cv; procedure found;
  comment u = cv: tested if u is known, else u is given the value cv for as long as found runs;
  if uk then
  begin if u = cv then found end
  else
  begin u := cv; uk := true; found; uk := false end equals;

  procedure answera;
  comment output adapter: one solution of A, the value of x;
  begin na := na + 1; outstring(1, "[answer]x = "); outinteger(1, xv); outstring(1, "[/answer]\n") end answera;

  procedure seconda;
  comment the second conjunct of A, once the first has given its solution;
  equals(xk, xv, c2, answera);

  procedure answerb;
  comment output adapter: one solution of B, the value of y;
  begin nb := nb + 1; outstring(1, "[answer]y = "); outinteger(1, yv); outstring(1, "[/answer]\n") end answerb;

  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  xk := yk := false;
  na := nb := 0;

  for i := 1 while true do
  begin
    comment harness words: one message, spawn computation c of stage k, and then the stage's constants;
    ininteger(0, code); ininteger(0, k); ininteger(0, c);
    ininteger(0, c1); ininteger(0, c2); ininteger(0, c3);
    if c = 1 then
    begin
      comment computation A: x = c1 and x = c2, with x unknown;
      equals(xk, xv, c1, seconda);
      outstring(1, "[observe]computation A ended\n");
      if na = 0 then outstring(1, "no solution\n");
      outstring(1, "[/observe]\n")
    end
    else if c = 2 then
    begin
      comment computation B: y = c3, with y unknown;
      equals(yk, yv, c3, answerb);
      outstring(1, "[observe]computation B ended\n");
      if nb = 0 then outstring(1, "no solution\n");
      outstring(1, "[/observe]\n")
    end;
    outstring(1, "[end]")
  end
end
