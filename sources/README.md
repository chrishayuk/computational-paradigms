# Sources

Copies of papers are not kept here. `sources/downloads/` is ignored by git.

## Where the problems come from

| problem | origin |
|---|---|
| P01 | Absys's suspended equations: E. W. Elcock, "Absys: the first logic programming language", *J. Logic Programming* 9(1) (1990), pp. 8–13; absys E01 |
| P02 | E. W. Elcock, "Goal selection strategies in Horn clause programming", *Proc. 4th Biennial Conf. CSCSI*, Saskatoon (1982), p. 123; absys E06 |
| P03 | the append and reverse examples of Elcock (1990), pp. 8–13; absys E01. The reverse here is the naive one, not Elcock's |
| P04 | absys E04 |
| P05 | written for this study, after the absys E07 engine session |
| P06 | Elcock (1990), pp. 14–15, the setdiff and student examples; K. L. Clark, "Negation as failure", in *Logic and Data Bases* (1978); absys E02 |
| P07 | Elcock (1982), p. 124, on linear equations; absys E09. P07e–g written for this study |
| P08 | absys E03 |
| P09 | written for this study. Absys has no counterpart |
| P10 | written for this study, after review 1: replacement and retraction, which imperative languages, PLANNER's erase and Conniver's contexts provide |
| P11 | written for this study, after review 1 |
| P12 | written for this study, after review 1, with solution depths placed by design; P12d after review 2 |
| P13 | written for this study, after review 1, in the manner of TPK: one fixed task in every system |
| P14 | the counter over a stream of messages, a standard idiom of stream-based concurrent logic programming: E. Y. Shapiro, "A subset of Concurrent Prolog and its interpreter", ICOT TR-003 (1983); and of process networks: G. Kahn, "The semantics of a simple language for parallel programming", IFIP 74 |
| P15 | merge is the standard example of nondeterminism in the same literature (Shapiro 1983; Kahn and MacQueen, "Coroutines and networks of parallel processes", IFIP 77); the resource grant is written for this study |
| P16 | written for this study, after review 2, for the case concurrent constraint programming was designed for: many relations told to one store. V. A. Saraswat, *Concurrent Constraint Programming*, MIT Press (1993) |

The absys experiments are in https://github.com/chrishayuk/absys,
`docs/research.md`. Most problems began there, and this is disclosed in
`SPECIFICATION.md`.

## Method

- D. E. Knuth and L. Trabb Pardo, *The Early Development of Programming
  Languages*, Stanford report STAN-CS-76-562 (1976). This is the model of
  one problem, written in each language's own style.

## Sources for later systems

These have not been gathered yet. Each system's folder will list the
sources its idioms are drawn from.
