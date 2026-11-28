begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays (5.2), recursive procedures and function designators with value and name parameters, a subscripted variable given as the actual parameter called by name and assigned to (4.7.3.2, 5.4), and procedures as actual parameters (4.7.5, 5.4.4), each solution being passed to a parameterless procedure in the way of the procedures passed as parameters in Knuth's man or boy test (1964, examples/man-or-boy-1964.alg in the image, cited after batch 1B's reading of it), a go to statement that leaves a deep recursion at once (4.3, examples/exits.alg in the image, cited after batch 1C's reading of it), the for statement (4.6) and conditional statements (4.5), the input and output procedures ininteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices (systems file, Values), the producer transcribed as batch 1C's P09d transcribes genu (programs/algol-60/README.md), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: L b1 ... bL e, the length and then the elements of the known sequence b of merge(b, z, m), and then e of position(e, m, i);
  comment P15b2. zeros(z) and merge(b, z, m) and position(e, m, i), in that order, any one: P15b with the arguments of merge swapped. zeros computes z by its one case, as a function, the direction the query uses: zeros(the sequence of 0 alone ++ s) if zeros(s), so z is the sequence of 0 alone followed by the z of zeros. The function must return before its cell can be made, and before merge can begin, and it never returns: ALGOL 60 has no infinite values and no lazy ones, so the greatest relation cannot be held, and the stream reading of P09d2 is not reached. merge is as in P15a, by its four cases in order, each solution m passed to the next conjunct. position computes i from e and m by its cases, in order, as a function, 0 meaning that it has no solution. Case 1: position(e, the sequence of e alone ++ t, 1). Case 2: position(e, the sequence of h alone ++ t, i) if h differs from e and position(e, t, j) and i = j + 1, its conjuncts in order. The first m for which position has a solution is reported, and the query is left there by a go to statement. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence of hd[c] alone ++ the sequence tl[c]. The store of 10000 cells is fixed in one place;
  integer n, cap, m, i, code, k, lb, e, top, z0, b0, mv, iv, nsol, zeros1, mg1, mg2, mg3, mg4, pos1, pos2;
  integer array hd, tl[1:10000];

  integer procedure cons(h, t);
    value h, t; integer h, t;
  comment a new cell, the sequence of h alone ++ the sequence t;
  begin top := top + 1; hd[top] := h; tl[top] := t; cons := top end cons;

  integer procedure readseq(len);
    value len; integer len;
  comment a sequence of len elements, read from the input in order;
  begin
    integer j, el, first, last, cl;
    first := last := 0;
    for j := 1 step 1 until len do
    begin
      ininteger(0, el); cl := cons(el, 0);
      if last = 0 then first := cl else tl[last] := cl;
      last := cl
    end;
    readseq := first
  end readseq;

  integer procedure zeros;
  comment zeros(z), computing z by its one case;
  begin
    integer s;
    zeros1 := zeros1 + 1;
    s := zeros;
    zeros := cons(0, s)
  end zeros;

  procedure merge(a, b, m, found);
    value a, b; integer a, b, m; procedure found;
  comment merge(a, b, m), m unknown, by its cases in order, each solution passed to found;
  begin
    integer c;
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
    end
  end merge;

  integer procedure position(e, m);
    value e, m; integer e, m;
  comment position(e, m, i), computing i by its cases, in order, 0 when it has no solution;
  if m = 0 then position := 0
  else if hd[m] = e then
  begin
    comment case 1;
    pos1 := pos1 + 1;
    position := 1
  end
  else
  begin
    integer j;
    comment case 2;
    pos2 := pos2 + 1;
    j := position(e, tl[m]);
    position := if j = 0 then 0 else j + 1
  end position;

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
  comment the next conjunct, position(e, m, i), for the m that merge has given. The first solution is reported, and the query is left there;
  begin
    iv := position(e, mv);
    if iv ≠ 0 then
    begin
      nsol := nsol + 1;
      outstring(1, "[answer]i = "); num(iv); outstring(1, "[/answer]\n");
      go to done
    end
  end found;

  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  top := nsol := zeros1 := mg1 := mg2 := mg3 := mg4 := pos1 := pos2 := 0;
  comment the stage's constants: the sequence b, and then e;
  ininteger(0, lb);
  b0 := readseq(lb);
  ininteger(0, e);

  comment the query: zeros(z) and merge(b, z, m) and position(e, m, i), in that order, any one;
  z0 := zeros;
  merge(b0, z0, mv, found);

  comment observe: reached only if zeros returns. The query comes here by the go to statement in found;
done:
  outstring(1, "[observe]");
  if nsol = 0 then outstring(1, "no solution\n");
  outstring(1, "[operations zeros/1 "); num(zeros1); outstring(1, "]\n");
  outstring(1, "[operations merge/1 "); num(mg1); outstring(1, "]\n");
  outstring(1, "[operations merge/2 "); num(mg2); outstring(1, "]\n");
  outstring(1, "[operations merge/3 "); num(mg3); outstring(1, "]\n");
  outstring(1, "[operations merge/4 "); num(mg4); outstring(1, "]\n");
  outstring(1, "[operations position/1 "); num(pos1); outstring(1, "]\n");
  outstring(1, "[operations position/2 "); num(pos2); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
end
