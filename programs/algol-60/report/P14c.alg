begin
  comment HARNESS POSING incremental;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for assignment statements (4.2), arrays (5.2), procedures (5.4), the for statement with a while element (4.6) and conditional statements (4.5), the input and output procedures ininteger and outstring as the interpreter gives them (IFIP 1964, systems file), atoms as integer codes (systems file, Values), a program that reads each stage as it arrives, which counts as the same computation (systems file, The same computation), and the message loop and observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS a line k for every stage k: the message the stage brings, as one code, 1 for INC and 2 for READ. The READ messages bind the unknowns r1, r2, r3 and so on, in the order they arrive;
  comment P14a, and P14c, which is its stages and two more. The counter is implemented as a process holding its count, which the problem allows as a transcription: the program itself, which reads each message as it arrives and answers before it reads the next. The count is the integer variable count, 0 at first, as the messages are posed with run(m, 0). Each message is taken by the case of run for its head, in the order the messages arrive. Case 2: INC, and the rest is run with count + 1, so count becomes count + 1. Case 3: READ(r), with r = count, and the rest is run with count, so r is given the count and count is unchanged. Case 1, run of the empty sequence, would close the stream, and no stage closes it. A message that is neither INC nor READ has no case of run, so run has no solution from that message on. The unknowns r1, r2 and so on are an integer array, at most 1000 of them, fixed in one place;
  integer n, cap, m, i, code, k, msg, count, nr, run2, run3;
  Boolean failed;
  integer array rv[1:1000];

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

  procedure receive(msg);
    value msg; integer msg;
  comment the counter receives one message: the case of run for the message at the head of the stream;
  if ¬failed then
  begin
    if msg = 1 then
    begin
      comment case 2: run(the sequence of INC alone ++ s, c) if run(s, c + 1);
      run2 := run2 + 1;
      count := count + 1
    end
    else if msg = 2 then
    begin
      comment case 3: run(the sequence of READ(r) alone ++ s, c) if r = c and run(s, c);
      run3 := run3 + 1;
      nr := nr + 1;
      rv[nr] := count
    end
    else
    begin
      comment no case of run has this message at its head;
      failed := true
    end
  end receive;

  comment harness words: the instance line;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  count := nr := run2 := run3 := 0;
  failed := false;

  for i := 1 while true do
  begin
    comment harness words: one message, and the stage it poses;
    ininteger(0, code); ininteger(0, k);
    comment the stage's constant: the message the counter receives;
    ininteger(0, msg);
    receive(msg);

    comment the answer: every unknown a READ has bound so far;
    if ¬failed then
    begin
      outstring(1, "[answer]");
      if nr = 0 then outstring(1, "no unknowns")
      else
      begin
        integer j;
        for j := 1 step 1 until nr do
        begin
          outstring(1, "r"); num(j); outstring(1, " = "); num(rv[j]);
          if j < nr then outstring(1, ", ")
        end
      end;
      outstring(1, "[/answer]\n")
    end;

    comment observe: the count held, the unknowns bound, and the applications of each case of run;
    outstring(1, "[observe]");
    if failed then outstring(1, "no solution: a message with no case of run\n");
    outstring(1, "count "); num(count); outstring(1, ", held in the running program, which waits on its next message\n");
    begin
      integer j;
      for j := 1 step 1 until nr do
      begin outstring(1, "[bind r"); num(j); outstring(1, "]"); num(rv[j]); outstring(1, "[/bind]\n") end
    end;
    outstring(1, "[operations run/2 "); num(run2); outstring(1, "]\n");
    outstring(1, "[operations run/3 "); num(run3); outstring(1, "]\n");
    outstring(1, "[/observe]\n[end]")
  end
end
