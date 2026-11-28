"""Classifier A's construct classes for algol-60 P04-P06, by line (report and x1
texts of a program share their line layout; x1sim texts are the x1 texts)."""

R_PROG = "rule 10: the program block (and blocks that size the encoding's arrays) that hold the transcription"
H_DECL = "harness README 2.7 items 4-5: declarations of variables holding only harness words, and of counters"
H_IN = "harness README 2.7 item 1: reads of the instance line and the message words"
H_LOOP = "harness README 2.7 item 2: the message loop and the dispatch on k (not the stage code it selects)"
H_OUT = "rule 13, harness README 2.7 item 3: output adapter / printed tags (answers and state already computed)"
H_CNT = "harness README 2.7 item 4: a counter that only counts (problem operations)"
P_CONST = "harness README 2.7 ('reading the constants: that is the stage information, P'); systems file, Values"
P_DECL = "the declaration of a value the problem's information or unknowns need (systems file, Values)"
P_ENC = "rule 15 and systems file, Values: the sequence encoding and its operations (construction, equality) are P"
P_TR = "rule 3: mode-faithful transcription of the problem's case, in the direction the query uses"
P_HEAD = "rule 2: a guard that tests only its case's own head is P"
P_QUERY = "class P: the query, as the problem states it"
P_UNK = "systems file, Values: the representation of an unknown (a Boolean that it has a value, an integer holding it)"
P_FACTS = "rule 6: the facts of a closed world that the problem states, looked up or enumerated in the order stated, are P"
R_CPS = "rules 3 and 5: an extra argument the problem does not give (the success continuation 'found')"
R_WRAP = "rules 3 and 5: a continuation procedure the problem does not give, wrapping a conjunct (the CPS form of the conjunction)"
R_DIR = "rule 3: code for a direction (mode) the query does not use"
R_MODE = "rule 3 (and rule 19's reading): the test of which places are known, so that one procedure serves several modes, is not the relation"
R_MOVE = "rule 4: a conjunct moved from the presentation order (one move, counted under reformulation); its contents classed on their own"
C_UNDO = "rule 2 (and rule 1): taking a binding back when found returns restores the state for the next alternative, i.e. the backtracking of the depth-first search; it changes both what is held and, in general, the solutions"
C_FREE = "rule 16: a reset that only lets store be reused (the cell made for a binding is given back)"
R_HOLD = "rule 19: code that holds the problem's own relations until x has values, and then decides them (R, core configuration)"
R_HOLDREC = "rule 19: what the holding records about a relation (posed, released), and the test of whether x is known"
P_EVAL = "rule 19: the evaluator's test of a fully known relation, or its computing of x from it, is P in every direction"

def P04ab():
    return [
        ('1', 'P', 'program block', R_PROG),
        ('8', 'H', 'declarations of harness words and of the counter loop1', H_DECL),
        ('8', 'P', 'declaration of the stage constant c1', P_DECL, 'c1', 'c1'),
        ('8', 'P', 'declaration of the value of x', P_UNK, 'xv', 'xv'),
        ('9', 'P', 'declaration of x has a value', P_UNK),
        ('11-12', 'P', 'loop: procedure heading', P_TR),
        ('11', 'R', 'continuation parameter found', R_CPS, 'found', 'found'),
        ('12', 'R', 'continuation parameter found', R_CPS, 'procedure', 'found'),
        ('14', 'P', 'loop case 1: loop(x) if loop(x)', P_TR),
        ('14', 'H', 'counter of loop case 1', H_CNT, 'loop1', '1'),
        ('14', 'R', 'continuation argument found', R_CPS, 'found', 'found'),
        ('16-17', 'P', 'equals (x = c): procedure heading', P_TR),
        ('16', 'R', 'continuation parameter found', R_CPS, 'found', 'found'),
        ('17', 'R', 'continuation parameter found', R_CPS, 'procedure', 'found'),
        ('19-21', 'R', 'equals: test whether x is known, and the branch for x known (never used: x is unknown whenever equals is called)', R_DIR),
        ('22', 'P', 'equals with x unknown: x := c', 'rule 8: equality written as an assignment in the direction the query uses'),
        ('22', 'R', 'success continuation call found', R_CPS, 'found', 'found'),
        ('22', 'C', 'x made unknown again when found returns', C_UNDO, 'xk#2', 'false'),
        ('24-30', 'H', 'answer: output adapter', H_OUT),
        ('33-35', 'H', 'reads of the instance line and the message', H_IN),
        ('37', 'P', 'read of the stage constant', P_CONST),
        ('38', 'P', 'x initially unknown', P_UNK),
        ('38', 'H', 'counter initialised', H_CNT, 'loop1', '$'),
        ('41', 'P', 'query: first alternative of the disjunction, in the order written', P_QUERY),
        ('41', 'R', 'continuation argument answer', R_CPS, 'answer', 'answer'),
        ('42', 'P', 'query: second alternative of the disjunction, in the order written', P_QUERY),
        ('42', 'R', 'continuation argument answer', R_CPS, 'answer', 'answer'),
        ('45-47', 'H', 'observe block', H_OUT),
        ('48', 'P', 'program block', R_PROG),
    ]

def conseq(L, used):
    """s = <a> ++ m, at line L. used: subset of {'TT','TF','FT'} (s known?, m known?)."""
    sp = [
        (f'{L}-{L+1}', 'P', 'conseq (s = <a> ++ m): procedure heading', P_TR),
        (f'{L}', 'R', 'continuation parameter found', R_CPS, 'found', 'found'),
        (f'{L+1}', 'R', 'continuation parameter found', R_CPS, 'procedure', 'found'),
    ]
    if 'TT' in used or 'TF' in used:
        sp += [
            (f'{L+3}-{L+4}', 'R', 'conseq: test whether s is known', R_MODE),
            (f'{L+5}-{L+8}', 'P', 'conseq, s known: the head tests s nonempty and hd[s] = a', P_HEAD),
            (f'{L+11}-{L+12}', 'P', 'conseq, s known: end of the head tests', P_HEAD),
            (f'{L+13}', 'R', 'conseq: end of the s-known branch', R_MODE),
        ]
        if 'TT' in used:
            sp += [(f'{L+9}', 'P', 'conseq, s and m known: test tl[s] = m', P_TR),
                   (f'{L+9}', 'R', 'conseq: test whether m is known', R_MODE, 'if', 'then'),
                   (f'{L+9}', 'R', 'success continuation call found', R_CPS, 'found', 'found')]
        else:
            sp += [(f'{L+9}', 'R', 'conseq, s and m known: a direction the query does not use', R_DIR)]
        if 'TF' in used:
            sp += [(f'{L+10}', 'P', 'conseq, s known, m unknown: m := tl[s]', P_TR),
                   (f'{L+10}', 'R', 'conseq: else of the test whether m is known', R_MODE, 'else', 'else'),
                   (f'{L+10}', 'R', 'success continuation call found', R_CPS, 'found', 'found'),
                   (f'{L+10}', 'C', 'm made unknown again when found returns', C_UNDO, 'mk#2', 'false')]
        else:
            sp += [(f'{L+10}', 'R', 'conseq, s known, m unknown: a direction the query does not use', R_DIR)]
    else:
        sp += [(f'{L+3}-{L+13}', 'R', 'conseq, s known (both branches): a direction the query does not use', R_DIR)]
    if 'FT' in used:
        sp += [(f'{L+14}', 'R', 'conseq: else, test whether m is known', R_MODE),
               (f'{L+15}', 'P', 'conseq, s unknown, m known: s := cons(a, m)', P_TR),
               (f'{L+15}', 'R', 'success continuation call found', R_CPS, 'found', 'found'),
               (f'{L+15}', 'C', 's made unknown again when found returns', C_UNDO, 'sk#2', 'false'),
               (f'{L+15}', 'C', 'the cell made for s given back', C_FREE, 'top', '1')]
    else:
        sp += [(f'{L+14}-{L+15}', 'R', 'conseq, s unknown, m known: a direction the query does not use', R_DIR)]
    return sp

def same(L, used):
    if used:
        return [(f'{L}-{L+3}', 'P', 'same: equality of two sequences', P_ENC)]
    return [(f'{L}-{L+3}', 'R', 'same: equality of two sequences, used only in a direction the query does not use', "rules 3, 14 and 15: an encoding operation used only in code for a direction the query does not use is R with it")]

def alist_left(L, known):
    """known: whether the query's s is known (P04c) or not (P04d)."""
    sp = [
        (f'{L}-{L+1}', 'P', 'alist (alist-left): procedure heading', P_TR),
        (f'{L}', 'R', 'continuation parameter found', R_CPS, 'found', 'found'),
        (f'{L+1}', 'R', 'continuation parameter found', R_CPS, 'procedure', 'found'),
        (f'{L+3}-{L+6}', 'P', 'alist case 1: block with its unknown m', P_TR),
        (f'{L+7}', 'R', 'procedure second: the second conjunct wrapped as a continuation', R_WRAP),
        (f'{L+9}', 'P', 'alist case 1, second conjunct: s = <a> ++ m', P_TR),
        (f'{L+9}', 'R', 'continuation argument found', R_CPS, 'found', 'found'),
        (f'{L+10}', 'H', 'counter of alist case 1', H_CNT),
        (f'{L+11}', 'P', 'm initially unknown', P_UNK),
        (f'{L+12}', 'P', 'alist case 1, first conjunct: alist(m), in the order written', P_TR),
        (f'{L+12}', 'R', 'continuation argument second', R_CPS, 'second', 'second'),
        (f'{L+13}', 'P', 'alist case 1: end of block', P_TR),
        (f'{L+14}', 'R', 'alist case 2: test whether s is known', R_MODE),
    ]
    if known:
        sp += [(f'{L+15}', 'P', 'alist case 2, s known: test s = <>', P_HEAD),
               (f'{L+15}', 'H', 'counter of alist case 2', H_CNT, 'al2', '1'),
               (f'{L+15}', 'R', 'success continuation call found', R_CPS, 'found', 'found')]
    else:
        sp += [(f'{L+15}', 'R', 'alist case 2, s known: a direction the query does not use', R_DIR)]
    sp += [
        (f'{L+16}', 'R', 'alist case 2: else of the test whether s is known', R_MODE),
        (f'{L+17}', 'P', 'alist case 2, s unknown: s := <>', P_TR),
        (f'{L+17}', 'H', 'counter of alist case 2', H_CNT, 'al2', '1'),
        (f'{L+17}', 'R', 'success continuation call found', R_CPS, 'found', 'found'),
        (f'{L+17}', 'C', 's made unknown again when found returns', C_UNDO, 'sk#2', 'false'),
        (f'{L+18}', 'P', 'alist: end of procedure', P_TR),
    ]
    return sp

def alist_right(L, known):
    sp = [
        (f'{L}-{L+1}', 'P', 'alist (alist-right): procedure heading', P_TR),
        (f'{L}', 'R', 'continuation parameter found', R_CPS, 'found', 'found'),
        (f'{L+1}', 'R', 'continuation parameter found', R_CPS, 'procedure', 'found'),
        (f'{L+3}', 'P', 'alist: begin of procedure body', P_TR),
        (f'{L+4}', 'R', 'alist case 1: test whether s is known', R_MODE),
        (f'{L+6}', 'R', 'alist case 1: else of the test whether s is known', R_MODE),
        (f'{L+8}-{L+10}', 'P', 'alist case 2: block with its unknown m', P_TR),
        (f'{L+17}', 'P', 'm initially unknown', P_UNK),
        (f'{L+20}-{L+21}', 'P', 'alist: end of case 2 block and of procedure', P_TR),
    ]
    if known:
        sp += [
            (f'{L+5}', 'P', 'alist case 1, s known: test s = <>', P_HEAD),
            (f'{L+5}', 'H', 'counter of alist case 1', H_CNT, 'al1', '1'),
            (f'{L+5}', 'R', 'success continuation call found', R_CPS, 'found', 'found'),
            (f'{L+7}', 'R', 'alist case 1, s unknown: a direction the query does not use', R_DIR),
            (f'{L+11}', 'R', 'procedure body: the body of case 2 wrapped as a continuation', R_WRAP),
            (f'{L+13}', 'R', 'procedure body: the body of case 2 wrapped as a continuation', R_WRAP),
            (f'{L+13}', 'H', 'counter of alist case 2', H_CNT, 'al2', '1'),
            (f'{L+13}', 'P', 'alist case 2 body: alist(m)', P_TR, 'alist', ')'),
            (f'{L+13}', 'R', 'continuation argument found', R_CPS, 'found', 'found'),
            (f'{L+14}-{L+16}', 'R', 'procedure head and its call of conseq: used only with s unknown, a direction the query does not use', R_DIR),
            (f'{L+18}', 'P', 'alist case 2, s known: its head s = <a> ++ m, then the body, in the order written', P_TR),
            (f'{L+18}', 'R', 'alist case 2: test whether s is known', R_MODE, 'if', 'then'),
            (f'{L+18}', 'R', 'continuation argument body', R_CPS, 'body', 'body'),
            (f'{L+19}', 'R', 'alist case 2, s unknown: a direction the query does not use', R_DIR),
        ]
    else:
        sp += [
            (f'{L+5}', 'R', 'alist case 1, s known: a direction the query does not use', R_DIR),
            (f'{L+7}', 'P', 'alist case 1, s unknown: s := <>', P_TR),
            (f'{L+7}', 'H', 'counter of alist case 1', H_CNT, 'al1', '1'),
            (f'{L+7}', 'R', 'success continuation call found', R_CPS, 'found', 'found'),
            (f'{L+7}', 'C', 's made unknown again when found returns', C_UNDO, 'sk#2', 'false'),
            (f'{L+11}-{L+13}', 'R', 'procedure body: used only with s known, a direction the query does not use', R_DIR),
            (f'{L+14}', 'R', 'procedure head: the head of case 2 wrapped as a continuation', R_WRAP),
            (f'{L+16}', 'P', 'alist case 2 head: s = <a> ++ m, decided after the body', P_TR),
            (f'{L+16}', 'R', 'continuation argument found', R_CPS, 'found', 'found'),
            (f'{L+18}', 'R', 'alist case 2, s known: a direction the query does not use', R_DIR),
            (f'{L+19}', 'R', 'alist case 2: else of the test whether s is known', R_MODE),
            (f'{L+19}', 'H', 'counter of alist case 2', H_CNT, 'al2', '1'),
            (f'{L+19}', 'P', 'alist case 2 body alist(m), called before the head is decided', R_MOVE, 'alist', ')'),
            (f'{L+19}', 'R', 'continuation argument head', R_CPS, 'head', 'head'),
        ]
    return sp

def P04_common_head(known):
    sp = [('1', 'P', 'program block', R_PROG),
          ('8', 'H', 'declarations of harness words', H_DECL),
          ('10-12', 'H', 'reads of the instance line and the message', H_IN)]
    if known:
        sp += [('8', 'P', 'declaration of the length of the known sequence', P_DECL, 'len', 'len'),
               ('14', 'P', "read of the stage's constant (the length of s)", P_CONST),
               ('15', 'P', 'block sizing the cells', R_PROG),
               ('16', 'P', 'declarations of the encoding (cell top, atom code) and of the value of s', P_ENC),
               ('16', 'H', 'declarations of counters', H_DECL, 'al1', 'al2'),
               ('17', 'P', 'declaration of s has a value', P_UNK),
               ('18', 'P', 'the arrays of the sequence encoding', P_ENC),
               ('20-23', 'P', 'cons: a new cell', P_ENC),
               ('25-38', 'P', "readseq: read the stage's sequence into the encoding", P_CONST)]
    else:
        sp += [('13', 'P', 'block of the encoding', R_PROG),
               ('14', 'P', 'declarations of the encoding (cell top, atom code) and of the value of s', P_ENC),
               ('14', 'H', 'declarations of counters', H_DECL, 'al1', 'al2'),
               ('15', 'P', 'declaration of s has a value', P_UNK),
               ('16', 'P', 'the arrays of the sequence encoding', P_ENC),
               ('18-21', 'P', 'cons: a new cell', P_ENC)]
    return sp

def P04_tail(L_answer_from, L_answer_to, L_init, L_query, L_obs, L_end, known):
    sp = [(f'{L_answer_from}-{L_answer_to}', 'H', 'answer (and printseq): output adapter', H_OUT),
          (f'{L_init}', 'P', 'encoding initialised: no cells yet', P_ENC),
          (f'{L_init}', 'H', 'counters initialised', H_CNT, 'al1', ':=#2'),
          (f'{L_init+1}', 'P', 'the atom a encoded as 1', P_ENC)]
    if known:
        sp += [(f'{L_init+2}', 'P', "s := the stage's sequence; s known", P_CONST)]
    else:
        sp += [(f'{L_init+2}', 'P', 's initially unknown', P_UNK)]
    sp += [(f'{L_query}', 'P', 'query alist(s)', P_QUERY),
           (f'{L_query}', 'R', 'continuation argument answer', R_CPS, 'answer', 'answer'),
           (f'{L_obs}-{L_obs+3}', 'H', 'observe block', H_OUT),
           (f'{L_end}-{L_end+1}', 'P', 'end of blocks', R_PROG)]
    return sp

def P04c():
    return (P04_common_head(True) + same(40, True) + conseq(45, {'TT', 'FT'}) + alist_left(62, True)
            + P04_tail(82, 84, 86, 91, 94, 98, True))

def P04d():
    return (P04_common_head(False) + same(23, False) + conseq(28, {'FT'}) + alist_left(45, False)
            + P04_tail(65, 82, 84, 89, 92, 96, False))

def P04e():
    return (P04_common_head(True) + same(40, False) + conseq(45, {'TF'}) + alist_right(62, True)
            + P04_tail(85, 87, 89, 94, 97, 101, True))

def P04f():
    return (P04_common_head(False) + same(23, False) + conseq(28, {'FT'}) + alist_right(45, False)
            + P04_tail(68, 85, 87, 92, 95, 99, False))

# ---------------- P05 ----------------
def P05(variant):
    """variant 'a' or 'c' (three stages, layout of P05a) or 'b'."""
    if variant in ('a', 'c'):
        rel = 'x > c2, x != c3' if variant == 'a' else 'x = c2, x = c3'
        sp = [
            ('1', 'P', 'program block', R_PROG),
            ('8', 'H', 'declarations of harness words and observe counters', H_DECL),
            ('8', 'P', "declarations of the fact index, the number of pick's facts and the stage constants", P_DECL, 'j', 'c3'),
            ('9', 'R', 'declarations of the holding flags (pick posed, each relation held)', R_HOLDREC),
            ('10', 'P', 'array of the values of x given by the facts of pick', P_FACTS),
            ('10', 'H', 'array of counters of the facts applied', H_CNT, 'pk', ']'),
            ('11', 'P', 'array: whether each value of x is still a solution', P_FACTS),
            ('13-25', 'R', 'test: the holding of the comparisons until pick has given x values, applied to every value held', R_HOLD),
            ('21', 'P', f'evaluator: the stage-2 relation ({rel.split(",")[0]}) tested on a known value; the value dropped if it fails', P_EVAL, 'if#2', 'false'),
            ('22', 'P', f'evaluator: the stage-3 relation ({rel.split(",")[1].strip()}) tested on a known value; the value dropped if it fails', P_EVAL, 'if#2', 'false'),
            ('27-51', 'H', 'digits and relations: output adapters', H_OUT),
            ('54-55', 'H', 'reads of the instance line', H_IN),
            ('56', 'R', 'holding state initialised: nothing posed, no values of x', R_HOLDREC),
            ('58-59', 'H', 'message loop', H_LOOP),
            ('61-62', 'H', 'message reads and dispatch on k', H_LOOP),
            ('63', 'P', 'stage 1, pick(x)', P_FACTS),
            ('65-67', 'P', "stage 1: each fact of pick, in order, gives x one value", P_FACTS),
            ('67', 'H', 'counter of the fact applied', H_CNT, 'pk', '1'),
            ('68', 'R', 'the holding records that x has values', R_HOLDREC),
            ('69', 'P', 'stage 1: end', P_FACTS),
            ('70', 'H', 'dispatch on k', H_LOOP),
            ('70', 'P', 'stage 2: the constant of the relation', P_CONST, 'begin', 'end'),
            ('70', 'R', 'the holding records the relation as posed', R_HOLDREC, 'r2', 'true'),
            ('71', 'H', 'dispatch on k', H_LOOP),
            ('71', 'P', 'stage 3: the constant of the relation', P_CONST, 'begin', 'end'),
            ('71', 'R', 'the holding records the relation as posed', R_HOLDREC, 'r3', 'true'),
            ('73', 'R', 'call of the holding: decide every held relation that can be decided', R_HOLD),
            ('76-114', 'H', 'answers and observe block: output adapters and counters', H_OUT),
            ('115', 'H', 'message loop end', H_LOOP),
            ('116', 'P', 'program block', R_PROG),
        ]
        return sp
    return [
        ('1', 'P', 'program block', R_PROG),
        ('8', 'H', 'declarations of harness words and observe counters', H_DECL),
        ('8', 'P', "declarations of the fact index, the number of pick's facts and the stage constant", P_DECL, 'j', 'c1'),
        ('9', 'R', 'declarations of the holding flags (pick posed, the relation held)', R_HOLDREC),
        ('10', 'P', 'array of the values of x given by the facts of pick', P_FACTS),
        ('10', 'H', 'array of counters of the facts applied', H_CNT, 'pk', ']'),
        ('11', 'P', 'array: whether each value of x is still a solution', P_FACTS),
        ('13-24', 'R', 'test: the holding of the comparison until pick has given x values, applied to every value held', R_HOLD),
        ('21', 'P', 'evaluator: x > c1 tested on a known value; the value dropped if it fails', P_EVAL, 'if#2', 'false'),
        ('26-41', 'H', 'digits and relations: output adapters', H_OUT),
        ('44-45', 'H', 'reads of the instance line', H_IN),
        ('46', 'R', 'holding state initialised: nothing posed, no values of x', R_HOLDREC),
        ('48-49', 'H', 'message loop', H_LOOP),
        ('51', 'H', 'message reads', H_LOOP),
        ('52', 'H', 'dispatch on k', H_LOOP),
        ('52', 'P', 'stage 1: the constant of x > c1', P_CONST, 'begin', 'end'),
        ('52', 'R', 'the holding records the relation as posed', R_HOLDREC, 'r1', 'true'),
        ('53', 'H', 'dispatch on k', H_LOOP),
        ('54', 'P', 'stage 2, pick(x)', P_FACTS),
        ('56-58', 'P', 'stage 2: each fact of pick, in order, gives x one value', P_FACTS),
        ('58', 'H', 'counter of the fact applied', H_CNT, 'pk', '1'),
        ('59', 'R', 'the holding records that x has values', R_HOLDREC),
        ('60', 'P', 'stage 2: end', P_FACTS),
        ('62', 'R', 'call of the holding: decide every held relation that can be decided', R_HOLD),
        ('65-103', 'H', 'answers and observe block: output adapters and counters', H_OUT),
        ('104', 'H', 'message loop end', H_LOOP),
        ('105', 'P', 'program block', R_PROG),
    ]

# ---------------- P06a/b/c ----------------
def neg_eval(L, i):
    """not (x = ci) evaluator, 7 lines from L (P06a: L=11, i=1; P06b: L=22, i=2)."""
    r = f'r{i}'
    return [
        (f'{L}', 'R', f'examine{i}: the evaluator of not (x = c{i}), a unit of the holding', R_HOLD),
        (f'{L+2}', 'R', f'examine{i}: begin', R_HOLD),
        (f'{L+3}', 'H', 'counter of examinations', H_CNT),
        (f'{L+4}', 'R', 'test whether x is known (with x unknown the negation waits)', R_HOLDREC),
        (f'{L+5}', 'P', f'evaluator: not (x = c{i}) tested with x known; inconsistent if it fails', P_EVAL),
        (f'{L+5}', 'R', 'the relation released once decided', R_HOLDREC, r, 'false'),
        (f'{L+5}', 'R', 'the relation released once decided', R_HOLDREC, f'{r}#2', 'false'),
        (f'{L+6}', 'R', f'examine{i}: end', R_HOLD),
    ]

def eq_eval(L, i):
    """x = ci evaluator, 10 lines from L (P06a: L=19, i=2; P06b: L=11, i=1)."""
    return [
        (f'{L}', 'R', f'examine{i}: the evaluator of x = c{i}, a unit of the holding', R_HOLD),
        (f'{L+2}', 'R', f'examine{i}: begin', R_HOLD),
        (f'{L+3}', 'H', 'counter of examinations', H_CNT),
        (f'{L+4}', 'R', 'test whether x is known', R_HOLDREC),
        (f'{L+5}', 'P', f'evaluator: x = c{i} tested with x known; inconsistent if it fails', P_EVAL),
        (f'{L+6}', 'R', 'else of the test whether x is known', R_HOLDREC),
        (f'{L+7}', 'P', f'evaluator: x computed from x = c{i}, x now known', P_EVAL),
        (f'{L+7}', 'R', 'the propagation told that x changed', R_HOLD, 'changed', 'true'),
        (f'{L+8}', 'R', 'the relation released once decided', R_HOLDREC),
        (f'{L+9}', 'R', f'examine{i}: end', R_HOLD),
    ]

def P06(variant):
    sp = [
        ('1', 'P', 'program block', R_PROG),
        ('8', 'H', 'declarations of harness words and observe counters', H_DECL),
        ('8', 'P', 'declarations of the stage constants and of the value of x', P_DECL, 'c1', 'xv'),
        ('8', 'R', 'declaration of the propagation loop variable', R_HOLD, 'pass', 'pass'),
        ('9', 'P', 'declarations: x has a value; the stages are inconsistent', P_UNK),
        ('9', 'R', 'declarations of the holding flags and of the propagation flag', R_HOLDREC, 'r1', 'changed'),
    ]
    if variant == 'b':
        sp += eq_eval(11, 1) + neg_eval(22, 2)
    else:
        sp += neg_eval(11, 1) + eq_eval(19, 2)
    sp += [
        ('30-40', 'R', 'propagate: every held relation examined, in the order posed, until a pass gives x no value', R_HOLD),
        ('42-51', 'H', 'relations: output adapter', H_OUT),
        ('54-55', 'H', 'reads of the instance line', H_IN),
        ('56', 'P', 'x initially unknown; not inconsistent', P_UNK),
        ('56', 'R', 'holding flags initialised', R_HOLDREC, 'r1', ':=#2'),
        ('57', 'H', 'counters initialised', H_CNT),
        ('59-60', 'H', 'message loop', H_LOOP),
        ('62', 'H', 'message reads', H_LOOP),
        ('63', 'H', 'dispatch on k', H_LOOP),
        ('63', 'P', 'stage 1: its constant', P_CONST, 'begin', 'end'),
        ('63', 'R', 'the holding records the relation as posed', R_HOLDREC, 'r1', 'true'),
        ('64', 'H', 'dispatch on k', H_LOOP),
        ('64', 'P', 'stage 2: its constant', P_CONST, 'begin', 'end'),
        ('64', 'R', 'the holding records the relation as posed', R_HOLDREC, 'r2', 'true'),
        ('66', 'R', 'call of the propagation', R_HOLD),
        ('69-90', 'H', 'answer and observe block: output adapters and counters', H_OUT),
        ('91', 'H', 'message loop end', H_LOOP),
        ('92', 'P', 'program block', R_PROG),
    ]
    return sp

def P06d():
    return [
        ('1', 'P', 'program block', R_PROG),
        ('8', 'H', 'declarations of harness words', H_DECL),
        ('8', 'P', 'declarations of the two lengths', P_DECL, 'l1', 'l2'),
        ('10-12', 'H', 'reads of the instance line and the message', H_IN),
        ('14', 'P', "reads of the stage's constants (the lengths)", P_CONST),
        ('15', 'P', 'block sizing the cells', R_PROG),
        ('16', 'P', 'declarations of the encoding and of the sequences s1, s2, d', P_ENC),
        ('16', 'H', 'declarations of counters', H_DECL, 'mem1', 'sd3'),
        ('17', 'P', 'the arrays of the sequence encoding', P_ENC),
        ('19-22', 'P', 'cons: a new cell', P_ENC),
        ('24-37', 'P', "readseq: read the stage's sequences into the encoding", P_CONST),
        ('39-46', 'P', 'mem(e, s) with both known, by its cases in order (a Boolean procedure: the direction the query uses)', P_TR),
        ('44', 'H', 'counter of mem case 1', H_CNT, 'mem1', '1'),
        ('46', 'H', 'counter of mem case 2', H_CNT, 'mem2', '1'),
        ('48-61', 'P', 'setdiff computing d from s1 and s2 by its cases in order, case 3 with the language negation of mem', P_TR),
        ('52', 'H', 'counter of setdiff case 1', H_CNT, 'sd1', '1'),
        ('54', 'H', 'counter of setdiff case 2', H_CNT, 'sd2', '1'),
        ('58', 'H', 'counter of setdiff case 3', H_CNT),
        ('63-72', 'H', 'printseq: output adapter', H_OUT),
        ('74', 'P', 'encoding initialised', P_ENC),
        ('74', 'H', 'counters initialised', H_CNT, 'mem1', ':=#5'),
        ('75-76', 'P', 's1 and s2 read from the stage', P_CONST),
        ('78', 'P', 'query setdiff(s1, s2, d)', P_QUERY),
        ('80-87', 'H', 'answer and observe block', H_OUT),
        ('88-89', 'P', 'end of blocks', R_PROG),
    ]

def P06e(open_query):
    sp = [('1', 'P', 'program block', R_PROG),
          ('8', 'H', 'declarations of harness words', H_DECL),
          ('8', 'P', 'declaration of the loop variable that also reads the facts', P_DECL, 'i', 'i'),
          ('10-12', 'H', 'reads of the instance line and the message', H_IN)]
    if not open_query:
        sp += [('8', 'P', 'declarations of the query atom and the numbers of facts', P_DECL, 'q', 'nt'),
               ('14-24', 'P', "reads of the stage's constants: the query atom, the facts of student and maths, blocks sizing their arrays", P_FACTS),
               ('25', 'H', 'declarations of counters', H_DECL),
               ('26', 'P', 'arrays of the facts of takes', P_FACTS),
               ('28-38', 'P', 'takes(p, c) with both known, tested on its facts in a closed world', P_FACTS),
               ('36', 'H', 'counter of takes facts matched', H_CNT, 'tak', '1'),
               ('40-63', 'P', 'nonmajor(p) with p known, by its one case, the conjuncts in order: student(p) tested on its facts, maths(k) enumerating its facts, not takes(p, k) with the language negation', P_TR),
               ('45', 'H', 'counter of nonmajor', H_CNT),
               ('50', 'H', 'counter of student facts', H_CNT),
               ('53', 'H', 'counter of maths facts', H_CNT, 'math', '1'),
               ('54', 'H', 'counter of negations decided', H_CNT),
               ('57-58', 'H', 'answer counter and the printed answer true', H_OUT),
               ('65', 'P', "read of the facts of takes", P_FACTS),
               ('66', 'H', 'counters initialised', H_CNT),
               ('69', 'P', 'query nonmajor(q)', P_QUERY),
               ('72-80', 'H', 'observe block', H_OUT),
               ('81-84', 'P', 'end of blocks', R_PROG)]
    else:
        sp += [('8', 'P', 'declarations of the numbers of facts', P_DECL, 'ns', 'nt'),
               ('14-23', 'P', "reads of the stage's constants: the facts of student and maths, blocks sizing their arrays", P_FACTS),
               ('24', 'H', 'declarations of counters', H_DECL),
               ('25', 'P', 'arrays of the facts of takes', P_FACTS),
               ('27-37', 'P', 'takes(p, c) with both known, tested on its facts in a closed world', P_FACTS),
               ('35', 'H', 'counter of takes facts matched', H_CNT, 'tak', '1'),
               ('39-44', 'H', 'printatom: output adapter', H_OUT),
               ('46-67', 'P', 'nonmajor(p) with p unknown, by its one case, the conjuncts in order: student(p) enumerating its facts, maths(k) enumerating its facts, not takes(p, k) with the language negation', P_TR),
               ('50', 'H', 'counter of nonmajor', H_CNT),
               ('53', 'H', 'counter of student facts', H_CNT, 'stud', '1'),
               ('57', 'H', 'counter of maths facts', H_CNT, 'math', '1'),
               ('58', 'H', 'counter of negations decided', H_CNT),
               ('61-62', 'H', 'answer counter and the printed answer p', H_OUT),
               ('69', 'P', "read of the facts of takes", P_FACTS),
               ('70', 'H', 'counters initialised', H_CNT),
               ('73', 'P', 'query nonmajor(p)', P_QUERY),
               ('76-84', 'H', 'observe block', H_OUT),
               ('85-88', 'P', 'end of blocks', R_PROG)]
    return sp

TEXTS = {
    'P04a': P04ab, 'P04b': P04ab, 'P04c': P04c, 'P04d': P04d, 'P04e': P04e, 'P04f': P04f,
    'P05a': lambda: P05('a'), 'P05b': lambda: P05('b'), 'P05c': lambda: P05('c'),
    'P06a': lambda: P06('a'), 'P06b': lambda: P06('b'), 'P06d': P06d,
    'P06e1': lambda: P06e(False), 'P06e3': lambda: P06e(True),
}
