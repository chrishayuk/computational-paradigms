begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), procedures and Boolean function designators (5.4), the Boolean operator of negation (3.4), the for statement (4.6) and conditional statements (4.5), the input and output procedures ininteger, outinteger and outstring as the interpreter gives them (IFIP 1964, systems file), facts as arrays of integer codes (systems file, Values), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line 1: q S s1 ... sS M m1 ... mM T p1 k1 ... pT kT. q is the atom of the query nonmajor(q). Then the facts of the closed world: S and the atom of each fact student(s), M and the atom of each fact maths(m), T and the two atoms of each fact takes(p, k), each in order. Atoms are integer codes: brown 1, smith 2, c101 101, c301 301, any other atom another positive integer;
  comment P06e1, and P06e2, which has the same stage with other constants. The query nonmajor(q) with q known, by the one case of nonmajor: nonmajor(p) if student(p) and maths(k) and not takes(p, k), the conjuncts in that order. student, maths and takes are given by their facts. student(q) is tested on each fact in order, maths(k) gives k the value of each fact in order, and takes(q, k), with both known, is tested on its facts. Each derivation is reported as one answer, true;
  integer n, cap, m, i, code, k, q, ns, nm, nt;
  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  comment the stage's constants: the atom of the query, and then each relation's facts, their number first, which sizes its array;
  ininteger(0, q);
  ininteger(0, ns);
  begin
  integer array st[1:ns];
  for i := 1 step 1 until ns do ininteger(0, st[i]);
  ininteger(0, nm);
  begin
  integer array mt[1:nm];
  for i := 1 step 1 until nm do ininteger(0, mt[i]);
  ininteger(0, nt);
  begin
  integer nm1, stud, math, tak, negs, found;
  integer array tp, tk[1:nt];

  Boolean procedure takes(p, c);
    value p, c; integer p, c;
  comment takes(p, c) with both known: true when one of its facts is takes(p, c), in a closed world;
  begin
    integer j;
    Boolean t;
    t := false;
    for j := 1 step 1 until nt do
    begin if tp[j] = p ∧ tk[j] = c then begin tak := tak + 1; t := true end end;
    takes := t
  end takes;

  procedure nonmajor(p);
    value p; integer p;
  comment nonmajor(p) with p known, by its one case, the conjuncts in order. Each derivation is one answer;
  begin
    integer a, b, kv;
    nm1 := nm1 + 1;
    for a := 1 step 1 until ns do
    begin
      if st[a] = p then
      begin
        stud := stud + 1;
        for b := 1 step 1 until nm do
        begin
          kv := mt[b]; math := math + 1;
          negs := negs + 1;
          if ¬takes(p, kv) then
          begin
            found := found + 1;
            outstring(1, "[answer]true[/answer]\n")
          end
        end
      end
    end
  end nonmajor;

  for i := 1 step 1 until nt do begin ininteger(0, tp[i]); ininteger(0, tk[i]) end;
  nm1 := stud := math := tak := negs := found := 0;

  comment the query: nonmajor(q);
  nonmajor(q);

  comment observe: whether there is a solution, and the applications of each relation;
  outstring(1, "[observe]");
  if found = 0 then outstring(1, "no solution\n");
  outstring(1, "each negation decided with p and k known\n");
  outstring(1, "[operations nonmajor/1 "); outinteger(1, nm1); outstring(1, "]\n");
  outstring(1, "[operations student-facts-matched "); outinteger(1, stud); outstring(1, "]\n");
  outstring(1, "[operations maths-facts-matched "); outinteger(1, math); outstring(1, "]\n");
  outstring(1, "[operations takes-facts-matched "); outinteger(1, tak); outstring(1, "]\n");
  outstring(1, "[operations negations-decided "); outinteger(1, negs); outstring(1, "]\n");
  outstring(1, "[/observe]\n[end]")
  end
  end
  end
end
