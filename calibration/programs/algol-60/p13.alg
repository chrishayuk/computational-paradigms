comment P13. Deterministic scale, n = 100. ALGOL 60, configuration report.
  From problems/13-deterministic-scale.md.
  Prescribed tasks (P13a-P13d): a sequence is a chain of cells in the
  parallel arrays hd and tl, as in p03.alg: hd[i] is the head, tl[i] the
  index of the tail, 0 the empty sequence. Taking the head or the tail is
  one subscript. Cells are never reclaimed, and the arrays are made large
  enough for rev, whose conc copies make n(n+1)/2 cells, and free is set
  back to 0 before each query.
  Native tasks (P13e, P13f): an integer array s[1:n], filled by a for
  statement, summed by a for statement, and reversed into a second array;
begin
  integer n;
  n := 100;
  begin
    integer array hd, tl[1 : n × n + 10 × n];
    integer free, s, r, k;

    integer procedure cons(h, t); value h, t; integer h, t;
    begin
      free := free + 1; hd[free] := h; tl[free] := t; cons := free
    end;

    comment s with range(m, n, s);
    integer procedure range(m, n); value m, n; integer m, n;
      range := if m > n then 0 else cons(m, range(m + 1, n));

    comment k with sum(s, k);
    integer procedure sum(s); value s; integer s;
    begin
      integer j;
      if s = 0 then sum := 0
      else
      begin
        j := sum(tl[s]); sum := hd[s] + j
      end
    end;

    comment c with conc(a, b, c);
    integer procedure conc(a, b); value a, b; integer a, b;
      conc := if a = 0 then b else cons(hd[a], conc(tl[a], b));

    comment b with rev(a, b), quadratic;
    integer procedure rev(a); value a; integer a;
    begin
      integer q;
      if a = 0 then rev := 0
      else
      begin
        q := rev(tl[a]); rev := conc(q, cons(hd[a], 0))
      end
    end;

    comment b with revacc(a, b);
    integer procedure revacc(a); value a; integer a;
      revacc := racc(a, 0);

    comment b with racc(a, c, b);
    integer procedure racc(a, c); value a, c; integer a, c;
      racc := if a = 0 then c else racc(tl[a], cons(hd[a], c));

    comment Harness (H): printing;
    procedure outseq(s); value s; integer s;
    begin
      outstring(1, "<");
    more:
      if s ≠ 0 then
      begin
        outinteger(1, hd[s]); s := tl[s]; go to more
      end;
      outstring(1, ">")
    end;

    free := 0;
    s := range(1, n);
    outstring(1, "p13a "); outseq(s); outstring(1, "\n");

    free := 0;
    s := range(1, n); k := sum(s);
    outstring(1, "p13b "); outinteger(1, k); outstring(1, "\n");

    free := 0;
    s := range(1, n); r := rev(s);
    outstring(1, "p13c "); outseq(r); outstring(1, "\n");

    free := 0;
    s := range(1, n); r := revacc(s);
    outstring(1, "p13d "); outseq(r); outstring(1, "\n")
  end;

  comment P13e, native;
  begin
    integer array s[1 : n];
    integer i, k;
    for i := 1 step 1 until n do s[i] := i;
    k := 0;
    for i := 1 step 1 until n do k := k + s[i];
    outstring(1, "p13e "); outinteger(1, k); outstring(1, "\n")
  end;

  comment P13f, native;
  begin
    integer array s, r[1 : n];
    integer i;
    for i := 1 step 1 until n do s[i] := i;
    for i := 1 step 1 until n do r[i] := s[n + 1 - i];
    outstring(1, "p13f <");
    for i := 1 step 1 until n do outinteger(1, r[i]);
    outstring(1, ">\n")
  end
end
