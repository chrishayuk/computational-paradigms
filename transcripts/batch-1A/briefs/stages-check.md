You are an independent checker. Your working directory is a clone of a public research repository: a frozen specification (`SPECIFICATION.md`, `PROTOCOL.md`, `problems/P01..P16`) and, under `harnesses/`, a stage table `harnesses/stages.json` and contract `harnesses/README.md` written by another agent. Read only files in this directory. Do not modify any file in it.

Check `harnesses/stages.json` against `problems/*.md`, problem by problem, sub-problem by sub-problem:
1. every sub-problem the problem file defines is present, and none is invented;
2. every stage is present, in order, with the right kind (adds / replaces / retracts / commit / query), and nothing is added;
3. each query's answer cap is 1 exactly where the problem file says the query asks for any one answer, and 20 otherwise;
4. commit stages (P11) and spawned computations (P09, P16) are flagged correctly;
5. the line numbers point at where each stage is stated;
6. sizes n, orders and readings listed match the problem file;
7. **no constant and no valid outcome of any problem appears** in stages.json (descriptions must use placeholders), except structural numbers such as n.
Also read `harnesses/QUESTIONS.md` and say, for each entry, whether you agree with the reading it implemented, briefly.

Write your findings to the file given in the final instruction, as a list: problem, sub-problem, stage, what is wrong, what the problem file says (with its line). End with a count of errors by kind, and the verdict: correct / correct with listed errors.
