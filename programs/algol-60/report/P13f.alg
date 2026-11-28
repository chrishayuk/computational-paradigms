begin
  comment HARNESS POSING reposed;
  comment PROVENANCE author: implementation-algol-60, an agent (Claude Opus 5.5, claude-opus-5-5);
  comment PROVENANCE precursor seen: no;
  comment PROVENANCE idioms: the Revised Report on ALGOL 60 (1962) for blocks and arrays whose bounds are computed at run time (5.2.4.2), and the for statement with a step-until element over the subscripts of an array (4.6, and its example in 4.6.1), the input and output procedures ininteger and outstring as the interpreter gives them (IFIP 1964, systems file), a sequence as an integer array with a length (systems file, Values), and the observe block of the harness README example X01 (harnesses/algol-60/README.md, 2.8);
  comment CONSTANTS none. n is the instance's size, from the instance line, and the sequence is the one of 1 to n that the problem names;
  comment P13f, native. The algorithm: the sequence of 1 to n is built in the integer array s[1:n] by a for statement, s[i] := i, and is held there until the answer is given. Then a second for statement makes its reverse in a second integer array r[1:n], r[i] := s[n + 1 - i]. Each loop takes n steps of the for statement, so the work is linear in n, and the store is the 2n elements of s and r;
  integer n, cap, m, i, code, k, size;
  comment harness words: the instance line, and the one message, which poses stage 1;
  ininteger(0, n); ininteger(0, cap); ininteger(0, m);
  for i := 1 step 1 until m do ininteger(0, code);
  ininteger(0, code); ininteger(0, k);
  size := if n < 1 then 1 else n;
  begin
  integer built, moved;
  integer array s, r[1:size];

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

  procedure printvec(len);
    value len; integer len;
  comment output adapter: the elements r[1] to r[len], in parentheses, separated by commas, with a new line after every ten elements so that no line of the X1 passes its 144 positions;
  begin
    integer j, c;
    outstring(1, "(");
    c := 0;
    for j := 1 step 1 until len do
    begin
      num(r[j]); c := c + 1;
      if j < len then outstring(1, ", ");
      if c = 10 then begin outstring(1, "\n"); c := 0 end
    end;
    outstring(1, ")")
  end printvec;

  built := moved := 0;

  comment build the sequence of 1 to n;
  for i := 1 step 1 until n do
  begin s[i] := i; built := built + 1 end;

  comment reverse it;
  for i := 1 step 1 until n do
  begin r[i] := s[n + 1 - i]; moved := moved + 1 end;

  outstring(1, "[answer]r = "); printvec(n); outstring(1, "[/answer]\n");
  comment observe: the elements built and moved, and the store held after the answer;
  outstring(1, "[observe]");
  outstring(1, "native: the sequence made in the vector s of n elements by one loop, and its reverse made in a second vector r by a second loop\n");
  outstring(1, "elements held after the answer: "); num(n + n); outstring(1, ", the vectors s and r, kept as long as the program runs\n");
  outstring(1, "elements built: "); num(built); outstring(1, ", elements moved: "); num(moved); outstring(1, "\n");
  outstring(1, "[/observe]\n[end]")
  end
end
