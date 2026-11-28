begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), recursive procedures with value and name parameters, a subscripted variable given as the actual parameter called by name and assigned to (4.7.3.2, 5.4), and procedures as actual parameters (4.7.5, 5.4.4), each solution being passed to a parameterless procedure in the way of the procedures passed as parameters in Knuth's man or boy test (1964, examples/man-or-boy-1964.alg in the image, cited after batch 1B's reading of it), a go to statement that leaves a deep recursion at once (4.3, examples/exits.alg in the image, cited after batch 1C's reading of it), the for statement (4.6) and conditional statements (4.5), the input and output procedures ininteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices (systems file, Values), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: La a1 ... aLa Lb b1 ... bLb, the length and then the elements of each of the two known sequences a and b of merge(a, b, m);
  comment P15a1. merge(a, b, m), any one, with a and b known and m unknown, by its four cases in order, as a procedure that passes each solution to the parameterless procedure found and returns when it has no more. Case 1: merge(the empty sequence, b, b). Case 2: merge(the sequence of h alone ++ a, the empty sequence, the sequence of h alone ++ a). Case 3: merge(the sequence of h alone ++ a, b, the sequence of h alone ++ m) if b is not empty and merge(a, b, m). Case 4: merge(a, the sequence of h alone ++ b, the sequence of h alone ++ m) if a is not empty and merge(a, b, m). In cases 3 and 4 the cell of m is made with its head h and its tail still to come, and the tail is passed by name to the recursive merge, which gives it its value in place, so m is complete whenever found runs. The cell is given back when the case is done. The query asks for any one answer, so found reports the first solution and leaves the recursion at once by a go to statement, and the cases not yet tried are not tried. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence of hd[c] alone ++ the sequence tl[c];
  integer n, cap, m, i, code, k, la;
  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constants: the first sequence, and then the second;
  ininteger(0, la);
  begin
  integer top, a0, b0, lb, mv, nsol, mg1, mg2, mg3, mg4, depth, peak;
  integer array hd, tl[1:2000];

  integer procedure cons(h, t);
    value h, t; integer h, t;
  comment a new cell, the sequence of h alone ++ the sequence t;
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

  procedure merge(a, b, m, found);
    value a, b; integer a, b, m; procedure found;
  comment merge(a, b, m), m unknown, by its cases in order, each solution passed to found;
  begin
    integer c;
    depth := depth + 1; if depth > peak then peak := depth;
    comment case 1: merge(the empty sequence, b, b);
    if a = 0 then
    begin mg1 := mg1 + 1; m := b; found end;
    comment case 2: merge(the sequence of h alone ++ a, the empty sequence, the sequence of h alone ++ a);
    if a ≠ 0 then
    begin
      if b = 0 then begin mg2 := mg2 + 1; m := a; found end
    end;
    comment case 3: merge(the sequence of h alone ++ a, b, the sequence of h alone ++ m) if b is not empty and merge(a, b, m);
    if a ≠ 0 then
    begin
      if b ≠ 0 then
      begin
        mg3 := mg3 + 1;
        c := cons(hd[a], 0);
        m := c;
        merge(tl[a], b, tl[c], found);
        top := top - 1
      end
    end;
    comment case 4: merge(a, the sequence of h alone ++ b, the sequence of h alone ++ m) if a is not empty and merge(a, b, m);
    if b ≠ 0 then
    begin
      if a ≠ 0 then
      begin
        mg4 := mg4 + 1;
        c := cons(hd[b], 0);
        m := c;
        merge(a, tl[b], tl[c], found);
        top := top - 1
      end
    end;
    depth := depth - 1
  end merge;

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

  procedure printseq(p);
    value p; integer p;
  comment output adapter: a sequence, its elements in parentheses, separated by commas, with a new line after every ten elements so that no line of the X1 passes its 144 positions;
  begin
    integer j, c;
    outstring(1, "(");
    c := 0;
    for j := 0 while p ≠ 0 do
    begin
      num(hd[p]); p := tl[p]; c := c + 1;
      if p ≠ 0 then outstring(1, ", ");
      if c = 10 then begin outstring(1, "\n"); c := 0 end
    end;
    outstring(1, ")")
  end printseq;

  procedure found;
  comment the first solution m of merge is reported, and the query is left there;
  begin
    nsol := nsol + 1;
    outstring(1, "[answer]m = "); printseq(mv); outstring(1, "[/answer]\n");
    go to done
  end found;

  top := nsol := mg1 := mg2 := mg3 := mg4 := depth := peak := 0;
  a0 := readseq(la);
  ininteger(0, lb);
  b0 := readseq(lb);

  comment the query: merge(a, b, m), any one;
  merge(a0, b0, mv, found);

  comment observe: the interleaving reported, the applications of each case, and what is held after it. The query comes here by the go to statement in found;
done:
  outstring(1, "[observe]");
  if nsol = 0 then outstring(1, "no solution\n");
  outstring(1, "one answer asked: interleavings reported "); num(nsol);
  outstring(1, ", depth first, by the cases in order\n");
  outstring(1, "recursion of merge at most "); num(peak); outstring(1, " deep, and the cases not yet tried, which the recursion kept, dropped by the jump out of the recursion\n");
  outstring(1, "[problem-alternatives interleavings 0]\n");
  outstring(1, "[operations merge/1 "); num(mg1); outstring(1, "]\n");
  outstring(1, "[operations merge/2 "); num(mg2); outstring(1, "]\n");
  outstring(1, "[operations merge/3 "); num(mg3); outstring(1, "]\n");
  outstring(1, "[operations merge/4 "); num(mg4); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
  end
end
