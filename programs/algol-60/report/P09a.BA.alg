begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), recursive procedures and function designators with value and name parameters (4.7, 5.4) and procedures as actual parameters (4.7.5, 5.4.4), each solution being passed to a parameterless procedure in the way of the procedures passed as parameters in Knuth's man or boy test (1964, examples/man-or-boy-1964.alg in the image), the for statement (4.6) and conditional statements (4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices (systems file, Values), and the message loop, spawn message and observe block of the harness README (harnesses/algol-60/README.md, 2.2, 2.6 and the example X01 of 2.8);
  comment CONSTANTS a line 1: L e1 ... eL, the length and then the elements of the known sequence of computation B, rev(that sequence, b). Elements are integers, an atom being its integer code. The harness sends the line after each spawn message of stage 1, so computation A reads it too, and does not use it;
  comment P09a. Two computations, spawned one after the other by the harness, in the instance's spawn order. A: loop(x), by loop's one case, loop(x) if loop(x), a procedure that calls itself, x unknown. B: rev(a, b) with a known, b computed from a by the cases of rev, in order, as a function, the direction this query uses, conc likewise computing its third place from the first two. ALGOL 60 has one computation only, so a spawned computation is a procedure of this program, run to its end before the next message is read. Both share the variables of the outer block. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence hd[c] followed by the sequence tl[c];
  integer n, cap, m, i, code, k, c, la, xv, loop1, conc1, conc2, rev1, rev2;
  Boolean xk;

  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  xk := false;
  loop1 := conc1 := conc2 := rev1 := rev2 := 0;

  for i := 1 while true do
  begin
    comment harness words: one message, spawn computation c of stage k, and then the stage's constants;
    ininteger(0, code); ininteger(0, k); ininteger(0, c);
    ininteger(0, la);
    begin
      integer top, a0, b0;
      integer array hd, tl[1:la + la × (la + 1) ÷ 2 + 1];

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

      integer procedure conc(a, b);
        value a, b; integer a, b;
      comment conc(a, b, c), computing c from a and b by its cases, in order. Case 1: conc(the empty sequence, b, b). Case 2: conc(h followed by a, b, h followed by c) if conc(a, b, c);
      if a = 0 then
      begin conc1 := conc1 + 1; conc := b end
      else
      begin
        integer cc;
        conc2 := conc2 + 1;
        cc := conc(tl[a], b);
        conc := cons(hd[a], cc)
      end conc;

      integer procedure rev(a);
        value a; integer a;
      comment rev(a, b), computing b from a by its cases, in order. Case 1: rev(the empty sequence, the empty sequence). Case 2: rev(h followed by l, r) if rev(l, q) and conc(q, the sequence of h alone, r), its conjuncts in that order;
      if a = 0 then
      begin rev1 := rev1 + 1; rev := 0 end
      else
      begin
        integer q;
        rev2 := rev2 + 1;
        q := rev(tl[a]);
        rev := conc(q, cons(hd[a], 0))
      end rev;

      procedure loop(xk, x, found);
        Boolean xk; integer x; procedure found;
      comment loop(x), by its one case: loop(x) if loop(x). Each solution would be passed to found;
      begin loop1 := loop1 + 1; loop(xk, x, found) end loop;

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
      comment output adapter: a sequence, its elements in parentheses, separated by commas;
      begin
        integer j;
        outstring(1, "(");
        for j := 0 while p ≠ 0 do
        begin num(hd[p]); p := tl[p]; if p ≠ 0 then outstring(1, ", ") end;
        outstring(1, ")")
      end printseq;

      procedure answera;
      comment output adapter: one solution of A, the value of x;
      begin
        outstring(1, "[answer]x");
        if xk then begin outstring(1, " = "); num(xv) end else outstring(1, " free");
        outstring(1, "[/answer]\n")
      end answera;

      top := 0;
      a0 := readseq(la);

      if c = 1 then
      begin
        comment computation A: loop(x), with x unknown;
        loop(xk, xv, answera);
        outstring(1, "[observe]computation A ended\n");
        outstring(1, "[operations loop/1 "); outinteger(1, loop1); outstring(1, "]\n");
        outstring(1, "[/observe]\n")
      end
      else if c = 2 then
      begin
        comment computation B: rev(a, b), with a known;
        b0 := rev(a0);
        outstring(1, "[answer]b = "); printseq(b0); outstring(1, "[/answer]\n");
        outstring(1, "[observe]computation B ended\n");
        outstring(1, "[bind b]"); printseq(b0); outstring(1, "[/bind]\n");
        outstring(1, "[operations rev/1 "); outinteger(1, rev1); outstring(1, "]\n");
        outstring(1, "[operations rev/2 "); outinteger(1, rev2); outstring(1, "]\n");
        outstring(1, "[operations conc/1 "); outinteger(1, conc1); outstring(1, "]\n");
        outstring(1, "[operations conc/2 "); outinteger(1, conc2); outstring(1, "]\n");
        outstring(1, "[/observe]\n")
      end
    end;
    outstring(1, "[end]")
  end
end
