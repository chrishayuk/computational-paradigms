begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), recursive procedures with value and name parameters, a subscripted variable given as the actual parameter called by name and assigned to (4.7.3.2, 5.4), and procedures as actual parameters (4.7.5, 5.4.4), each solution being passed to a parameterless procedure in the way of the procedures passed as parameters in Knuth's man or boy test (1964, examples/man-or-boy-1964.alg in the image), the depth-first enumeration of a space by a recursive procedure, as in Wirth's eight queens (1971, examples/queens.alg in the image), a go to statement that leaves a deep recursion at once (4.3, examples/exits.alg in the image), the for statement (4.6) and conditional statements (4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices and facts as arrays of codes (systems file, Values), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: F, the number of facts of accept, and then each fact, its length L and its L atoms, in order. The atom l is the code 1, the atom r the code 2. The size n and the answer mode come from the harness, not from the constants;
  comment P12. One stage: choice(n, s) and accept(s), in that order, s unknown. choice is transcribed by its cases, in order, as a procedure that passes each of its solutions to the procedure found, and returns when it has no more. Case 1: choice(n, the empty sequence). Case 2: choice(n, the sequence of e alone ++ t) if n is greater than 0 and (e = l or e = r, in that order) and choice(n - 1, t). The head of case 2 makes the cell of s, with its tail t to come, and t is the tail of that cell, passed by name to the recursive call, which gives it its value. accept is a closed world of facts, tested on each s that choice gives, fact by fact in order, by the equality of sequences. Each fact equal to s is one solution. For a query for any one answer, the instance's cap 1, the search is left at the first solution. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence hd[c] followed by the sequence tl[c]. The store is fixed at 2000 cells for the facts, in one place, and n + 1 more for the search;
  integer n, cap, m, i, code, k;
  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  begin
  integer top, lcode, rcode, nfacts, f, len, sv, nsol, cand, ch1, ch2, depth, peakdepth, pend, peakpend;
  Boolean anyone;
  integer array hd, tl[0:2000 + n + 1], fact[1:2000];

  integer procedure cons(h, t);
    value h, t; integer h, t;
  comment a new cell, the sequence h followed by the sequence t;
  begin top := top + 1; hd[top] := h; tl[top] := t; cons := top end cons;

  integer procedure readseq(len);
    value len; integer len;
  comment a sequence of len elements, read from the input in order;
  begin
    integer j, e, first, last, cl;
    first := last := 0;
    for j := 1 step 1 until len do
    begin
      ininteger(0, e); cl := cons(e, 0);
      if last = 0 then first := cl else tl[last] := cl;
      last := cl
    end;
    readseq := first
  end readseq;

  Boolean procedure same(p, q);
    value p, q; integer p, q;
  comment the equality of two sequences;
  same := if p = 0 then q = 0 else if q = 0 then false else if hd[p] = hd[q] then same(tl[p], tl[q]) else false;

  procedure choice(n, s, found);
    value n; integer n, s; procedure found;
  comment choice(n, s), s unknown, by its cases in order, each solution passed to found;
  begin
    integer c;
    comment case 1: choice(n, the empty sequence);
    ch1 := ch1 + 1;
    s := 0;
    found;
    comment case 2: choice(n, the sequence of e alone ++ t) if n is greater than 0 and (e = l or e = r) and choice(n - 1, t);
    if n > 0 then
    begin
      c := cons(0, 0);
      s := c;
      depth := depth + 1; if depth > peakdepth then peakdepth := depth;
      pend := pend + 1; if pend > peakpend then peakpend := pend;
      ch2 := ch2 + 1;
      hd[c] := lcode;
      choice(n - 1, tl[c], found);
      pend := pend - 1;
      ch2 := ch2 + 1;
      hd[c] := rcode;
      choice(n - 1, tl[c], found);
      depth := depth - 1;
      top := top - 1
    end
  end choice;

  procedure printseq(p);
    value p; integer p;
  comment output adapter: a sequence, its atoms in parentheses, separated by commas, l and r by name;
  begin
    integer j;
    outstring(1, "(");
    for j := 0 while p ≠ 0 do
    begin
      if hd[p] = lcode then outstring(1, "l") else if hd[p] = rcode then outstring(1, "r") else outinteger(1, hd[p]);
      p := tl[p];
      if p ≠ 0 then outstring(1, ", ")
    end;
    outstring(1, ")")
  end printseq;

  procedure accept;
  comment accept(s), for the s that choice has given, by its facts in order. Each fact equal to s is one solution, and is reported. A query for any one answer is left at the first;
  begin
    integer f;
    cand := cand + 1;
    for f := 1 step 1 until nfacts do
    begin
      if same(sv, fact[f]) then
      begin
        nsol := nsol + 1;
        outstring(1, "[answer]s = "); printseq(sv); outstring(1, "[/answer]\n");
        outstring(1, "candidates examined so far: "); outinteger(1, cand); outstring(1, "\n");
        if anyone then go to done
      end
    end
  end accept;

  top := 0;
  lcode := 1; rcode := 2;
  anyone := cap = 1;
  nsol := cand := ch1 := ch2 := depth := peakdepth := pend := peakpend := 0;

  comment the stage's constants: the facts of accept;
  ininteger(0, nfacts);
  for f := 1 step 1 until nfacts do
  begin
    ininteger(0, len);
    fact[f] := readseq(len)
  end;

  comment the query: choice(n, s) and accept(s), in that order;
  choice(n, sv, accept);

  comment observe: the candidates examined, the applications of each case of choice, and the partial sequences held. A query for any one answer comes here by the go to statement in accept;
done:
  outstring(1, "[observe]");
  if nsol = 0 then outstring(1, "no solution\n");
  if anyone then outstring(1, "a query for any one answer\n") else outstring(1, "a query for all answers\n");
  outstring(1, "[candidates "); outinteger(1, cand); outstring(1, "]\n");
  outstring(1, "[operations choice/1 "); outinteger(1, ch1); outstring(1, "]\n");
  outstring(1, "[operations choice/2 "); outinteger(1, ch2); outstring(1, "]\n");
  outstring(1, "partial sequence held, depth first: at most "); outinteger(1, peakdepth);
  outstring(1, " cells, with at most "); outinteger(1, peakpend); outstring(1, " alternatives e = r kept for backtracking\n");
  outstring(1, "[problem-alternatives partial-sequences 0]\n");
  outstring(1, "[/observe]\n[end]")
  end
end
