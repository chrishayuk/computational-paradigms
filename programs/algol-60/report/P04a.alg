begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for recursive procedures with parameters called by name (4.7.3.2, 5.4) and procedures as actual parameters (4.7.5, 5.4.4), each solution being passed to a parameterless procedure in the way of the procedures passed as parameters in Knuth's man or boy test (1964, examples/man-or-boy-1964.alg in the image), conditional statements (4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: k, the integer of the alternative x = k;
  comment P04a. The query loop(x) or x = k, its alternatives in that order. loop is transcribed by its one case, loop(x) if loop(x): a procedure that calls itself. Each relation is a procedure that passes each of its solutions to the procedure found, and returns when it has no more. x is a Boolean that says whether it has a value, and an integer that holds it. The alternatives are tried in the order written, the second when the first has returned;
  integer n, cap, m, i, code, k, c1, xv, loop1;
  Boolean xk;

  procedure loop(xk, x, found);
    Boolean xk; integer x; procedure found;
  comment loop(x), by its one case: loop(x) if loop(x);
  begin loop1 := loop1 + 1; loop(xk, x, found) end loop;

  procedure equals(xk, x, c, found);
    value c; Boolean xk; integer x, c; procedure found;
  comment x = c: tested if x is known, else x is given the value c for as long as found runs;
  if xk then
  begin if x = c then found end
  else
  begin x := c; xk := true; found; xk := false end equals;

  procedure answer;
  comment output adapter: one solution, the value of x;
  begin
    outstring(1, "[answer]x");
    if xk then begin outstring(1, " = "); outinteger(1, xv) end else outstring(1, " free");
    outstring(1, "[/answer]\n")
  end answer;

  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constant;
  ininteger(0, c1);
  xk := false; loop1 := 0;

  comment the query: loop(x) or x = c1, in that order;
  loop(xk, xv, answer);
  equals(xk, xv, c1, answer);

  comment observe: the applications of the case of loop;
  outstring(1, "[observe]");
  outstring(1, "[operations loop/1 "); outinteger(1, loop1); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
end
