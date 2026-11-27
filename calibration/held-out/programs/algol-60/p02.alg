comment P02. Late information -- ALGOL 60, configuration "report".

  A held-out calibration program (a development example, not a result).
  Author: Claude (Opus 5.5), as an agent.  Written from
  problems/02-late-information.md.  The author has not seen any precursor
  program (the absys experiments E01-E09) or any other program written for
  this study.

  The stages are read from standard input (p02.in) with ininteger, one
  computation per run, so each stage arrives into the computation that is
  already running (systems/algol-60/README.md, "The same computation").
  The input is the one place the stage constants are kept (PROTOCOL.md,
  rule 6).  Its encoding, part of transcribing the stages:
    number of runs,
    per run: which sub-problem (1 = P02a, 2 = P02b, 3 = P02c), number of
      stages,
    per stage: number of relations, then each relation as
      1 c     R1: u + v = c
      2       R2: w x u = v
      3 a b   R3: u + a = b.

  Layout, for the classifiers:
    1. The unknowns u, v, w, with a Boolean each saying whether it is known.
    2. The relations rel1, rel2, rel3, one procedure each, transcribing R1,
       R2, R3 in every direction the stages need.  Each returns a verdict:
         0 waits (cannot be decided yet),
         1 binds the unknown numbered which (1 u, 2 v, 3 w) to val,
         2 holds for every value of its remaining unknowns (decided),
         3 fails (no solutions).
    3. The held relations, in arrival order (kind, constants, alive), and
       resume, which takes every held relation up again when a stage
       arrives, until a whole pass decides nothing new.  Written for this
       problem's relations only.  ALGOL 60 has no unknowns and no suspended
       relations, so the program keeps them itself: reformulation.
    4. solutions12, a reformulation used only for the report: R1 and R2
       together, with nothing known, have finitely many integer solutions.
    5. Output adapters (showrel, showwaits, report) and the reading of the
       stages, which stand in for the harness (pose, print).

  What is reported after each stage: the unknowns bound and unbound, the
  relations still held with known values put in (a residual, read from
  the program's own arrays, which the next stage acts on), the solutions as
  values where R1 and R2 alone are held with nothing known, or "no
  solutions" where a relation fails.  An infinite outcome is therefore
  bindings plus held relations: solved form where nothing is held,
  residual otherwise;

begin
  comment 1. The unknowns;
  integer u, v, w;
  Boolean ku, kv, kw;

  comment The verdict's binding;
  integer which, val;

  comment 3. The held relations, in arrival order;
  integer array kind, ca, cb[1:30];
  Boolean array alive[1:30];
  integer nrel;
  Boolean failed;

  comment Examinations of each relation in the current stage (for the
    observations only);
  integer array examined[1:3];

  integer runs, run, id, nstages, stage, nr, j, code;

  comment 2. The relations;

  integer procedure rel1(c); value c; integer c;
    comment R1: u + v = c;
  begin
    if ku ∧ kv then
    begin
      if u + v = c then rel1 := 2 else rel1 := 3
    end
    else if ku then
    begin which := 2; val := c - u; rel1 := 1 end
    else if kv then
    begin which := 1; val := c - v; rel1 := 1 end
    else rel1 := 0
  end rel1;

  integer procedure rel2;
    comment R2: w × u = v;
  begin
    if kw ∧ ku ∧ kv then
    begin
      if w × u = v then rel2 := 2 else rel2 := 3
    end
    else if kw ∧ ku then
    begin which := 2; val := w × u; rel2 := 1 end
    else if ku ∧ kv then
    begin
      comment u × w = v, w unknown;
      if u = 0 then
      begin
        if v = 0 then rel2 := 2 else rel2 := 3
      end
      else if v ÷ u × u = v then
      begin which := 3; val := v ÷ u; rel2 := 1 end
      else rel2 := 3
    end
    else if kw ∧ kv then
    begin
      comment w × u = v, u unknown;
      if w = 0 then
      begin
        if v = 0 then rel2 := 2 else rel2 := 3
      end
      else if v ÷ w × w = v then
      begin which := 1; val := v ÷ w; rel2 := 1 end
      else rel2 := 3
    end
    else if ku then
    begin
      if u = 0 then begin which := 2; val := 0; rel2 := 1 end
      else rel2 := 0
    end
    else if kw then
    begin
      if w = 0 then begin which := 2; val := 0; rel2 := 1 end
      else rel2 := 0
    end
    else rel2 := 0
  end rel2;

  integer procedure rel3(a, b); value a, b; integer a, b;
    comment R3: u + a = b;
  begin
    if ku then
    begin
      if u + a = b then rel3 := 2 else rel3 := 3
    end
    else
    begin which := 1; val := b - a; rel3 := 1 end
  end rel3;

  comment 3. Taking up the held relations;

  integer procedure examine(i); value i; integer i;
  begin
    if kind[i] = 1 then examine := rel1(ca[i])
    else if kind[i] = 2 then examine := rel2
    else examine := rel3(ca[i], cb[i])
  end examine;

  procedure bind;
  begin
    if which = 1 then begin u := val; ku := true end
    else if which = 2 then begin v := val; kv := true end
    else begin w := val; kw := true end
  end bind;

  procedure resume;
  begin
    integer i, r;
    Boolean progress;
  again:
    progress := false;
    for i := 1 step 1 until nrel do
      if alive[i] ∧ ¬failed then
      begin
        r := examine(i);
        examined[kind[i]] := examined[kind[i]] + 1;
        trace(i, r);
        if r = 1 then begin bind; progress := true end
        else if r = 2 then begin alive[i] := false; progress := true end
        else if r = 3 then failed := true
      end;
    if progress ∧ ¬failed then go to again
  end resume;

  comment 4. Reformulation, for the report only.  By R1, v = c - u.  Put in
    R2, w × u = c - u, so u × (w + 1) = c.  If c is not 0, u divides c,
    and each divisor d gives u = d, v = c - d, w = c ÷ d - 1.  Not in the
    problem file;

  procedure solutions12(c); value c; integer c;
  begin
    integer d, m, n, s;
    m := if c < 0 then -c else c;
    n := 0;
    for d := 1 step 1 until m do
      if c ÷ d × d = c then n := n + 2;
    outstring(1, "  outcome:  explicit, ");
    outinteger(1, n);
    outstring(1, "solutions (u, v, w):\n");
    for d := 1 step 1 until m do
      if c ÷ d × d = c then
      begin
        for s := d, -d do
        begin
          outstring(1, "            ");
          outinteger(1, s); outinteger(1, c - s); outinteger(1, c ÷ s - 1);
          outstring(1, "\n")
        end
      end
  end solutions12;

  comment 5. Output adapters;

  procedure showu; if ku then outinteger(1, u) else outstring(1, "u ");
  procedure showv; if kv then outinteger(1, v) else outstring(1, "v ");
  procedure showw; if kw then outinteger(1, w) else outstring(1, "w ");

  procedure showwaits(k); value k; integer k;
  begin
    outstring(1, "waits on ");
    if k = 2 ∧ ¬kw then outstring(1, "w ");
    if ¬ku then outstring(1, "u ");
    if k ≠ 3 ∧ ¬kv then outstring(1, "v ")
  end showwaits;

  procedure showrel(i); value i; integer i;
  begin
    outstring(1, "R"); outinteger(1, kind[i]); outstring(1, ": ");
    if kind[i] = 1 then
    begin
      showu; outstring(1, "+ "); showv; outstring(1, "= "); outinteger(1, ca[i])
    end
    else if kind[i] = 2 then
    begin
      showw; outstring(1, "× "); showu; outstring(1, "= "); showv
    end
    else
    begin
      showu; outstring(1, "+ "); outinteger(1, ca[i]);
      outstring(1, "= "); outinteger(1, cb[i])
    end
  end showrel;

  procedure trace(i, r); value i, r; integer i, r;
  begin
    outstring(1, "  trace:    R"); outinteger(1, kind[i]);
    if r = 0 then showwaits(kind[i])
    else if r = 1 then
    begin
      outstring(1, "binds ");
      if which = 1 then outstring(1, "u") else if which = 2 then
        outstring(1, "v") else outstring(1, "w");
      outstring(1, " = "); outinteger(1, val)
    end
    else if r = 2 then outstring(1, "decided")
    else outstring(1, "fails");
    outstring(1, "\n")
  end trace;

  procedure report;
  begin
    integer i, nalive, c;
    Boolean has1, has2;
    outstring(1, "  examined: ");
    for i := 1 step 1 until 3 do
      if examined[i] > 0 then
      begin
        outstring(1, "R"); outinteger(1, i); outinteger(1, examined[i])
      end;
    outstring(1, "\n");
    if failed then outstring(1, "  outcome:  no solutions\n")
    else
    begin
      outstring(1, "  bound:    ");
      if ku then begin outstring(1, "u = "); outinteger(1, u) end;
      if kv then begin outstring(1, "v = "); outinteger(1, v) end;
      if kw then begin outstring(1, "w = "); outinteger(1, w) end;
      if ¬ku ∧ ¬kv ∧ ¬kw then outstring(1, "none");
      outstring(1, "\n  unbound:  ");
      if ¬ku then outstring(1, "u ");
      if ¬kv then outstring(1, "v ");
      if ¬kw then outstring(1, "w ");
      if ku ∧ kv ∧ kw then outstring(1, "none");
      outstring(1, "\n");
      nalive := 0; has1 := has2 := false; c := 0;
      for i := 1 step 1 until nrel do
        if alive[i] then
        begin
          nalive := nalive + 1;
          if kind[i] = 1 then begin has1 := true; c := ca[i] end;
          if kind[i] = 2 then has2 := true;
          outstring(1, "  held:     "); showrel(i);
          outstring(1, "  "); showwaits(kind[i]); outstring(1, "\n")
        end;
      if nalive = 0 then
      begin
        outstring(1, "  held:     none\n");
        if ku ∧ kv ∧ kw then outstring(1, "  outcome:  explicit\n")
        else outstring(1, "  outcome:  solved form (the unbound are free)\n")
      end
      else if nalive = 2 ∧ has1 ∧ has2 ∧ ¬ku ∧ ¬kv ∧ ¬kw ∧ c ≠ 0 then
        solutions12(c)
      else outstring(1, "  outcome:  residual (the held relations above)\n")
    end
  end report;

  comment Stand-in for the harness: read and pose each stage;

  ininteger(0, runs);
  for run := 1 step 1 until runs do
  begin
    ininteger(0, id); ininteger(0, nstages);
    nrel := 0; ku := kv := kw := false; failed := false;
    for stage := 1 step 1 until nstages do
    begin
      for j := 1 step 1 until 3 do examined[j] := 0;
      if id = 1 then outstring(1, "P02a") else if id = 2 then
        outstring(1, "P02b") else outstring(1, "P02c");
      outstring(1, " stage "); outinteger(1, stage); outstring(1, ":");
      ininteger(0, nr);
      for j := 1 step 1 until nr do
      begin
        ininteger(0, code);
        nrel := nrel + 1; kind[nrel] := code; alive[nrel] := true;
        if code = 1 then ininteger(0, ca[nrel])
        else if code = 3 then
        begin ininteger(0, ca[nrel]); ininteger(0, cb[nrel]) end;
        outstring(1, " R"); outinteger(1, code)
      end;
      outstring(1, "\n");
      resume;
      report
    end;
    outstring(1, "\n")
  end
end
