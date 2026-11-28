begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for assignment statements as replacement (4.2), arrays (5.2), recursive procedures and function designators with value parameters (4.7, 5.4), the for statement with a while element (4.6) and conditional statements (4.5), the input and output procedures ininteger and outstring as the interpreter gives them (IFIP 1964, systems file), atoms as integer codes and sequences as parallel arrays of heads and tail indices (systems file, Values), named quantities as variables, as batch 1C's P10a holds them (programs/algol-60/README.md), a program that reads each stage as it arrives, which counts as the same computation (systems file, The same computation), and the message loop and observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line k for every stage k: r p, what the stage brings, r being 1 for a request and 2 for a release, and p the code of the atom that makes it, A being 1 and B being 2;
  comment P15d. holder and queue are named quantities, each one variable: holder an atom code, 0 for none, and queue a sequence. They start as none and the empty sequence. Each stage replaces them by its case, by assignment, the right sides taken at the values before the stage. p requests: if holder = none, holder becomes p, otherwise queue becomes queue ++ the sequence of p alone. p releases, where holder = p: if queue is empty, holder becomes none, otherwise, with queue = the sequence of h alone ++ t, holder becomes h and queue becomes t. A release by someone who is not the holder is not one the problem defines: the program reports no solution and leaves holder and queue as they were. A grant once made is not withdrawn: a later request only joins the queue. A sequence is a cell index into the arrays hd and tl, 0 being the empty sequence, and a cell c being the sequence of hd[c] alone ++ the sequence tl[c]. ++ makes a new sequence by the cases of conc, as in P03, copying its first place. The store of 10000 cells is fixed in one place;
  integer n, cap, m, i, code, k, r, p, holder, queue, top, conc1, conc2, req1, req2, rel1, rel2;
  Boolean undefined;
  integer array hd, tl[1:10000];

  integer procedure cons(h, t);
    value h, t; integer h, t;
  comment a new cell, the sequence of h alone ++ the sequence t;
  begin top := top + 1; hd[top] := h; tl[top] := t; cons := top end cons;

  integer procedure conc(a, b);
    value a, b; integer a, b;
  comment a ++ b, by the cases of conc, in order. Case 1: conc(the empty sequence, b, b). Case 2: conc(the sequence of h alone ++ a, b, the sequence of h alone ++ c) if conc(a, b, c);
  if a = 0 then
  begin conc1 := conc1 + 1; conc := b end
  else
  begin
    integer c;
    conc2 := conc2 + 1;
    c := conc(tl[a], b);
    conc := cons(hd[a], c)
  end conc;

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

  procedure printseq(s);
    value s; integer s;
  comment output adapter: a sequence of atom codes, in parentheses, separated by commas, with a new line after every ten;
  begin
    integer j, c;
    outstring(1, "(");
    c := 0;
    for j := 0 while s ≠ 0 do
    begin
      num(hd[s]); s := tl[s]; c := c + 1;
      if s ≠ 0 then outstring(1, ", ");
      if c = 10 then begin outstring(1, "\n"); c := 0 end
    end;
    outstring(1, ")")
  end printseq;

  procedure printholder;
  comment output adapter: the holder, as its atom code, or none;
  if holder = 0 then outstring(1, "none") else num(holder);

  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  top := conc1 := conc2 := req1 := req2 := rel1 := rel2 := 0;
  holder := 0; queue := 0;

  for i := 1 while true do
  begin
    comment harness words: one message, and the stage it poses;
    ininteger(0, code); ininteger(0, k);
    comment the stage's constants: a request or a release, and who makes it;
    ininteger(0, r); ininteger(0, p);
    undefined := false;
    if r = 1 then
    begin
      comment p requests;
      if holder = 0 then
      begin req1 := req1 + 1; holder := p end
      else
      begin req2 := req2 + 1; queue := conc(queue, cons(p, 0)) end
    end
    else if r = 2 then
    begin
      comment p releases, where holder = p;
      if holder ≠ p then undefined := true
      else if queue = 0 then
      begin rel1 := rel1 + 1; holder := 0 end
      else
      begin rel2 := rel2 + 1; holder := hd[queue]; queue := tl[queue] end
    end
    else undefined := true;

    comment the answer: the values holder and queue have now;
    if ¬undefined then
    begin
      outstring(1, "[answer]holder = "); printholder; outstring(1, ", queue = "); printseq(queue); outstring(1, "[/answer]\n")
    end;

    comment observe: the one value held for each named quantity, and how the waiting requests are held;
    outstring(1, "[observe]");
    if undefined then outstring(1, "no solution: a stage the problem does not define, holder and queue left as they were\n");
    outstring(1, "atoms as codes: A is 1, B is 2, and none is 0\n");
    outstring(1, "holder and queue are variables, replaced by assignment, and their earlier values are not kept\n");
    outstring(1, "waiting requests: the atoms in queue, held as its elements, to be granted by a later release\n");
    outstring(1, "[bind holder]"); printholder; outstring(1, "[/bind]\n");
    outstring(1, "[bind queue]"); printseq(queue); outstring(1, "[/bind]\n");
    outstring(1, "[operations request/1 "); num(req1); outstring(1, "]\n");
    outstring(1, "[operations request/2 "); num(req2); outstring(1, "]\n");
    outstring(1, "[operations release/1 "); num(rel1); outstring(1, "]\n");
    outstring(1, "[operations release/2 "); num(rel2); outstring(1, "]\n");
    outstring(1, "[operations conc/1 "); num(conc1); outstring(1, "]\n");
    outstring(1, "[operations conc/2 "); num(conc2); outstring(1, "]\n");
    outstring(1, "[/observe]\n[end]")
  end
end
