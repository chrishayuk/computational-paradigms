begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), recursive procedures with parameters called by name (4.7.3.2, 5.4) and procedures as actual parameters (4.7.5, 5.4.4), each solution being passed to a parameterless procedure declared in an inner block, in the way of the procedure B passed as a parameter in Knuth's man or boy test (1964, examples/man-or-boy-1964.alg in the image), the for statement (4.6) and conditional statements and expressions (3.3, 4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), sequences as parallel arrays of heads and tail indices (systems file, Values), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: L e1 ... eL, the length and then the elements of the known sequence of the query alist(s). An atom is its integer code: the atom a of the definition is 1, any other atom another integer;
  comment P04c. The query alist(s) with s known, and the definition alist-left. Each relation is a procedure that passes each of its solutions to the procedure found, and returns when it has no more. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence hd[c] followed by the sequence tl[c]. An unknown sequence is a Boolean that says whether it has a value and an integer that holds it. The cases are tried in the order written, and the conjuncts of case 1 in the order written, so that alist(m) is called with m unknown before s = a ++ m is decided. A value given to an unknown is taken back when found returns, and a cell made for it is given back;
  integer n, cap, m, i, code, k, len;
  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constants: the length of s, which sizes the cells, and then its elements;
  ininteger(0, len);
  begin
  integer top, acode, sv, al1, al2;
  Boolean sk;
  integer array hd, tl[0:len + 20000];

  integer procedure cons(h, t);
    value h, t; integer h, t;
  comment a new cell, the sequence h followed by the sequence t;
  begin top := top + 1; hd[top] := h; tl[top] := t; cons := top end cons;

  integer procedure readseq(len);
    value len; integer len;
  comment a sequence of len elements, read from the input in order;
  begin
    integer j, e, first, last, c;
    first := last := 0;
    for j := 1 step 1 until len do
    begin
      ininteger(0, e); c := cons(e, 0);
      if last = 0 then first := c else tl[last] := c;
      last := c
    end;
    readseq := first
  end readseq;

  Boolean procedure same(p, q);
    value p, q; integer p, q;
  comment the equality of two sequences;
  same := if p = 0 then q = 0 else if q = 0 then false else if hd[p] = hd[q] then same(tl[p], tl[q]) else false;

  procedure conseq(sk, s, mk, m, found);
    Boolean sk, mk; integer s, m; procedure found;
  comment the equation s = the sequence of a alone ++ m, by the places known. With s known, it gives m its value, or tests it. With s unknown and m known, it gives s its value. Each solution is passed to found. With both unknown it does nothing: that is not reached here, since case 1 decides it only after alist(m) has given m;
  if sk then
  begin
    if s ≠ 0 then
    begin
      if hd[s] = acode then
      begin
        if mk then begin if same(tl[s], m) then found end
        else begin m := tl[s]; mk := true; found; mk := false end
      end
    end
  end
  else if mk then
  begin s := cons(acode, m); sk := true; found; sk := false; top := top - 1 end conseq;

  procedure alist(sk, s, found);
    Boolean sk; integer s; procedure found;
  comment alist-left, its cases in order. Case 1: alist(s) if alist(m) and s = the sequence of a alone ++ m, with the two conjuncts in that order. Case 2: alist(the empty sequence);
  begin
    begin
      integer m;
      Boolean mk;
      procedure second;
      comment the second conjunct of case 1, once alist(m) has given m;
      conseq(sk, s, mk, m, found);
      al1 := al1 + 1;
      mk := false;
      alist(mk, m, second)
    end;
    if sk then
    begin if s = 0 then begin al2 := al2 + 1; found end end
    else
    begin al2 := al2 + 1; s := 0; sk := true; found; sk := false end
  end alist;

  procedure answer;
  comment output adapter: one solution. The query has no unknowns, so a solution is true;
  outstring(1, "[answer]true[/answer]\n");

  top := al1 := al2 := 0;
  acode := 1;
  sv := readseq(len); sk := true;

  comment the query: alist(s), with s known;
  alist(sk, sv, answer);

  comment observe: the applications of each case of alist;
  outstring(1, "[observe]");
  outstring(1, "[operations alist/1 "); outinteger(1, al1); outstring(1, "]\n");
  outstring(1, "[operations alist/2 "); outinteger(1, al2); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
  end
end
