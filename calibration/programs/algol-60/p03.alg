comment P03. Reversible relations. ALGOL 60, configuration report.
  From problems/03-reversible-relations.md, with conc from
  problems/01-unknown-equality.md.
  A sequence is a chain of cells in the parallel arrays hd and tl: cell i
  holds the head hd[i] and the index tl[i] of the tail, and 0 is the empty
  sequence (systems/algol-60/README.md, Values).
  A procedure computes in one direction. conc and rev are transcribed by
  cases in the direction of P03a and P03e. Each other direction is a
  separate procedure, by the same cases read in that direction, which
  passes every solution it finds to the procedure given as found;
begin
  integer array hd, tl[1 : 1000];
  integer free;

  integer procedure cons(h, t); value h, t; integer h, t;
  begin
    free := free + 1; hd[free] := h; tl[free] := t; cons := free
  end;

  Boolean procedure same(x, y); value x, y; integer x, y;
    same := if x = 0 then y = 0
            else if y = 0 then false
            else hd[x] = hd[y] ∧ same(tl[x], tl[y]);

  comment P03a: c with conc(a, b, c), a and b given;
  integer procedure conc(a, b); value a, b; integer a, b;
    conc := if a = 0 then b else cons(hd[a], conc(tl[a], b));

  comment P03b: every a, b with conc(a, b, c), c given. Reformulation;
  procedure splits(c, found); value c; integer c; procedure found;
  begin
    procedure prefixed(a, b); value a, b; integer a, b;
      found(cons(hd[c], a), b);
    found(0, c);
    if c ≠ 0 then splits(tl[c], prefixed)
  end;

  comment P03c: every b with conc(a, b, c), a and c given. Reformulation;
  procedure suffix(a, c, found); value a, c; integer a, c; procedure found;
  begin
    if a = 0 then found(c)
    else if c ≠ 0 then
    begin
      if hd[c] = hd[a] then suffix(tl[a], tl[c], found)
    end
  end;

  comment P03d: every a with conc(a, b, c), b and c given. Reformulation;
  procedure prefix(b, c, found); value b, c; integer b, c; procedure found;
  begin
    procedure prefixed(a); value a; integer a;
      found(cons(hd[c], a));
    if same(b, c) then found(0);
    if c ≠ 0 then prefix(b, tl[c], prefixed)
  end;

  comment P03e: b with rev(a, b), a given;
  integer procedure rev(a); value a; integer a;
    rev := if a = 0 then 0 else conc(rev(tl[a]), cons(hd[a], 0));

  comment P03f: every a with rev(a, r), r given. Reformulation: case 2
    read backwards, with conc(q, <h>, r) taken before rev(l, q);
  procedure revinverse(r, found); value r; integer r; procedure found;
  begin
    procedure last(q, x); value q, x; integer q, x;
    begin
      procedure prefixed(l); value l; integer l;
        found(cons(hd[x], l));
      if x ≠ 0 then
      begin
        if tl[x] = 0 then revinverse(q, prefixed)
      end
    end;
    if r = 0 then found(0);
    splits(r, last)
  end;

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

  procedure show(s); value s; integer s;
  begin
    outstring(1, " "); outseq(s)
  end;

  procedure showpair(a, b); value a, b; integer a, b;
  begin
    outstring(1, " ("); outseq(a); outstring(1, ", "); outseq(b);
    outstring(1, ")")
  end;

  free := 0;

  outstring(1, "p03a "); outseq(conc(cons(1, cons(2, 0)), cons(3, 0)));
  outstring(1, "\n");

  outstring(1, "p03b");
  splits(cons(1, cons(2, 0)), showpair);
  outstring(1, "\n");

  outstring(1, "p03c");
  suffix(cons(1, 0), cons(1, cons(2, cons(3, 0))), show);
  outstring(1, "\n");

  outstring(1, "p03d");
  prefix(cons(3, 0), cons(1, cons(2, cons(3, 0))), show);
  outstring(1, "\n");

  outstring(1, "p03e "); outseq(rev(cons(1, cons(2, cons(3, 0)))));
  outstring(1, "\n");

  outstring(1, "p03f");
  revinverse(cons(1, cons(2, cons(3, 0))), show);
  outstring(1, "\n")
end
