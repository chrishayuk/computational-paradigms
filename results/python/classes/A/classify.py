# Classifier A, python, batch 1A: classes every token of every distinct text
# (results/python/tokens/TEXTS.tsv) by construct, and writes the "tokens" part
# of python.json (as tokens.json beside this script). Run with python3 -I.
#
# How spans are made. Each source line that carries tokens is looked up by its
# enclosing top-level scope (def/class name, or <top>) and the text of its
# tokens; the table below gives its class, construct and rule, either for the
# whole line or as segments starting at token offsets within the line (offsets
# count the line's tokens without its leading INDENT/DEDENT). A line's leading
# INDENT/DEDENT tokens go with the construct before them (the block header they
# open, or the block they close); its NEWLINE goes with its last segment.
# Inside any non-H segment, a harness read `s . constants [ "..." ]` or
# `s . params [ ... ]` (and the separator before it, rule 20) is carved out as H
# (harnesses/python/README.md, section 7, item 3).
import csv, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keys import texts, load, scopes, linekey

H_CONST = ("H", "harness read of s.constants / s.params", "harnesses/python/README.md s.7 item 3; METRICS rule 20 for the separator")

# ---------------------------------------------------------------- shorthands
def W(cls, construct, rule):           # whole line
    return [(0, cls, construct, rule)]

R19H = "METRICS rule 19 (holding code for the problem's own relations: R)"
R19E = "METRICS rule 19, evaluator split (computing a place / testing a fully known relation: P)"
R19T = "METRICS rule 19, evaluator split (tests of which places are known, the verdict to wait: R)"
HAD = "METRICS rule 13 (output adapter: H)"
HCALL = "harnesses/python/README.md s.7 (H constructs)"
CTH = "METRICS class C (thread calls, synchronisation, explicit scheduling)"
R14 = "METRICS rules 3 and 14 (separately written function for a direction: R throughout)"
P3 = "METRICS rule 3 (mode-faithful transcription: P)"
SINFO = "METRICS class P (the information of a stage)"
S12 = "METRICS rule 12 (code written for the experiment: S)"
S19 = "METRICS rules 12, 15 and 19 (program's own general mechanism: S)"
P15 = "METRICS rule 15 (operations on the sequence encoding: P)"

def posted(prefix_cls, prefix_con, prefix_rule, ntoks_prefix, suffix=None):
    """A statement `f ( <P information> )`: the wrapper call's first tokens and its
    closing paren are one class, the argument is the stage's information (P)."""
    def make(toks):
        n = len(toks)
        segs = [(0, prefix_cls, prefix_con, prefix_rule), (ntoks_prefix, "P", "stage information posted", SINFO)]
        # closing paren of the wrapper (and NEWLINE) back to the wrapper class
        segs.append((n - 2 if toks[-1] == "<NEWLINE>" else n - 1, prefix_cls, prefix_con, prefix_rule))
        return segs
    return make

def qwait(toks):
    # q . wait ( Relation ( "R1" , plus , ( u , v , K ) ) ) NEWLINE
    n = len(toks)
    return [(0, "C", "suspension call q.wait (freeze)", "METRICS class C (coroutine and freeze calls)"),
            (4, "R", "Relation wrapper (holding)", R19H),
            (6, "P", "the relation posted: name, evaluator, places", SINFO),
            (n - 3, "R", "Relation wrapper (holding)", R19H),
            (n - 2, "C", "suspension call q.wait (freeze)", "METRICS class C (coroutine and freeze calls)")]

def failed_append_rendered(toks):
    # failed . append ( <rendering> ) NEWLINE
    n = len(toks)
    return [(0, "P", "record that the stage's relation does not hold", "METRICS rule 1 (changes the report on an inconsistent stage)"),
            (4, "H", "rendering of the failed relation for print", HAD),
            (n - 2, "P", "record that the stage's relation does not hold", "METRICS rule 1")]

# ---------------------------------------------------------------- the table
T = {}
def put(scope, key, spec, where=None):
    T[(where, scope, key)] = spec

# constants block entries: stage information
for k in ['BACKWARDS = ( 1 , 2 , 3 )', 'FIRST = ( 1 , )', 'FIRST = ( 1 , 2 )', 'FORWARDS = ( 1 , 2 , 3 )',
          'PREFIX = ( 1 , )', 'PREFIX = ( 1 , 2 )', 'R1_SUM = 16', 'R3_ADDEND = 10', 'R3_SUM = 12',
          'SECOND = ( 3 , )', 'S_VALUE = ( 3 , )', 'WHOLE = ( 1 , 2 )', 'WHOLE = ( 1 , 2 , 3 )', 'Z_VALUE = 2']:
    put("<top>", k, W("P", "constants block entry (stage information)", "harnesses/python/README.md s.7 (block entries are the stages' information, classed by the rules); METRICS class P"))

for k in ['UNKNOWNS = ( "s" , "t" )', 'UNKNOWNS = ( "u" , "v" , "w" )', 'UNKNOWNS = ( "x" , "y" , "z" )', 'UNKNOWNS = ( "x" , )']:
    put("<top>", k, W("H", "order of unknowns for printing answers", HAD))

for k in ['EVALUATOR = { "R1" : plus , "R2" : times , "R3" : plus }', 'RELATION = { "=" : equal }',
          'RELATION = { "conc" : conc_places , "=" : equal }', 'RELATION = { "conc" : conc_places }']:
    put("<top>", k, W("R", "dispatch table from a held relation to its evaluator", R19H))

put("<top>", 'NIL = ( )', W("P", "encoding of the empty sequence", P15))
put("<top>", 'binder = Queue ( )', W("S", "instance of the S suspension queue, used for bind", S12))
put("<top>", 'q = Queue ( )', W("S", "instance of the S suspension queue", S12))
put("<top>", 'trail = [ ]', W("S", "trail of the program's unify/search", S19))
put("<top>", 'stack = [ ]', W("H", "list exposing the search's pending choice points for observe()", "harnesses/README.md s.11 point 5; METRICS rule 13"))
put("<top>", 'changed = threading . Condition ( )', W("C", "condition variable for the relation threads", CTH))
put("<top>", 'count = { "busy" : 0 , "news" : 0 }', W("C", "thread bookkeeping (busy threads, bindings made)", CTH))
put("<top>", 'import threading', W("C", "import of threading (external mechanism)", "METRICS rule 12 and class C (thread calls); listed as external mechanism"))
put("<top>", 'from S . search import search , undo', W("S", "import of S mechanism search", S12))
put("<top>", 'from S . suspend import Var , Queue , deref', W("S", "import of S mechanism suspend", S12))

for k in ['a , b = Var ( "a" ) , Var ( "b" )', 'a = Var ( "a" )', 'b = Var ( "b" )', 'c = Var ( "c" )']:
    put("<top>", k, W("P", "the query's unknowns", "METRICS class P (the query)"))
for k in ['s_ , t = Var ( "s" ) , Var ( "t" )', 'u , v , w = Var ( "u" ) , Var ( "v" ) , Var ( "w" )',
          'x , y , z = Var ( "x" ) , Var ( "y" ) , Var ( "z" )', 'x = Var ( "x" )']:
    put("<top>", k, W("P", "the problem's unknowns as logic variables", "METRICS class P"))
for k in ['unknowns = { "s" : s_ , "t" : t }', 'unknowns = { "u" : u , "v" : v , "w" : w }',
          'unknowns = { "x" : x , "y" : y , "z" : z }', 'unknowns = { "x" : x }', 'shown = { }']:
    put("<top>", k, W("H", "name -> unknown map, for cp.bindings and printing", HAD))

# cp calls, stage loop
for k in ['while ( s := cp . stage ( ) ) is not None :']:
    put("<top>", k, W("H", "stage loop header", HCALL + " item 1"))
for k in ['if s . k == 1 :', 'elif s . k == 2 :', 'elif s . k == 3 :', 'if not s . replay :']:
    put("<top>", k, W("H", "stage dispatch / replay test", HCALL + " items 2-3"))
for k in ['name = s . params [ "order" ] [ s . k - 1 ]', 'if name == "R1" :', 'elif name == "R2" :', 'elif name == "R3" :']:
    put("<top>", k, W("H", "dispatch on the relation the instance's order brings at this stage", HCALL + " items 2-3 (read of s.params, stage dispatch)"))
for (sc, k) in [x for x in [("<top>", l) for l in []]]:
    pass

# generic: any top-level line beginning with "cp ." is an H call (filled in at lookup)

put("<top>", 'if failed :', W("P", "report of no solution when a relation is found not to hold", "METRICS rules 1 and 13 (decides which result is reported: not an adapter)"))
for k in ['print ( "no solution: these equations do not hold:" , failed )', 'print ( "no solution: these relations do not hold:" , failed )']:
    put("<top>", k, W("H", "printing the no-solution report", HAD))
put("<top>", 'elif known :', W("H", "guard: print nothing while no unknown has a value", HAD))
put("<top>", 'else :', W("P", "else of the no-solution test", "METRICS rule 10 (connective of the if on failed)"))
for k in ['told = [ "%s = %d" % ( n , deref ( x ) ) for n , x in unknowns . items ( ) if not isinstance ( deref ( x ) , Var ) ]',
          'told = [ "%s = %s" % ( n , show ( v ) ) for n , v in unknowns . items ( ) if deref ( v ) is not v ]',
          'if told :', 'for n , v in unknowns . items ( ) :', 'shown [ n ] = show ( v )']:
    put("<top>", k, W("H", "rendering of the bindings already computed", HAD))

# core / stdlib: holding stores, posting
put("<top>", 'known = { }', W("R", "store of the values the holding code decides", R19H))
put("<top>", 'held = [ ]', W("R", "list of held relations", R19H))
put("<top>", 'waiting = [ ]', W("R", "list of relations whose threads wait", R19H))
put("<top>", 'failed = [ ]', W("R", "relations the holding code found not to hold", R19H))
put("<top>", 'decide ( )', W("R", "taking up the held relations", R19H))
put("<top>", 'settle ( )', W("C", "waiting until no relation thread is busy", CTH))
for k in ['held . append ( ( "=" , ( "s" , s . constants [ "S_VALUE" ] ) ) )', 'held . append ( ( "R1" , ( "u" , "v" , s . constants [ "R1_SUM" ] ) ) )',
          'held . append ( ( "R2" , ( "w" , "u" , "v" ) ) )', 'held . append ( ( "R3" , ( "u" , s . constants [ "R3_ADDEND" ] , s . constants [ "R3_SUM" ] ) ) )',
          'held . append ( ( "conc" , ( s . constants [ "PREFIX" ] , "s" , "t" ) ) )', 'held . append ( ( "x" , "y" ) )',
          'held . append ( ( "y" , "z" ) )', 'held . append ( ( "z" , s . constants [ "Z_VALUE" ] ) )',
          'held . append ( ( s . constants [ "PREFIX" ] , "x" , "x" ) )']:
    put("<top>", k, posted("R", "holding the stage's relation (held.append)", R19H, 4))
for k in ['pose ( ( "=" , ( "s" , s . constants [ "S_VALUE" ] ) ) )', 'pose ( ( "=" , ( "x" , "y" ) ) )', 'pose ( ( "=" , ( "y" , "z" ) ) )',
          'pose ( ( "=" , ( "z" , s . constants [ "Z_VALUE" ] ) ) )', 'pose ( ( "R1" , ( "u" , "v" , s . constants [ "R1_SUM" ] ) ) )',
          'pose ( ( "R2" , ( "w" , "u" , "v" ) ) )', 'pose ( ( "R3" , ( "u" , s . constants [ "R3_ADDEND" ] , s . constants [ "R3_SUM" ] ) ) )',
          'pose ( ( "conc" , ( s . constants [ "PREFIX" ] , "s" , "t" ) ) )', 'pose ( ( "conc" , ( s . constants [ "PREFIX" ] , "x" , "x" ) ) )']:
    put("<top>", k, posted("C", "giving the stage's relation a thread (pose)", CTH, 2))

# extended: posting
for k in ['q . wait ( Relation ( "R1" , plus , ( u , v , s . constants [ "R1_SUM" ] ) ) )', 'q . wait ( Relation ( "R2" , times , ( w , u , v ) ) )',
          'q . wait ( Relation ( "R3" , plus , ( u , s . constants [ "R3_ADDEND" ] , s . constants [ "R3_SUM" ] ) ) )']:
    put("<top>", k, qwait)
put("<top>", 'q . run ( )', W("C", "running the woken goals (S queue's scheduler)", "METRICS class C (explicit scheduling)"))
for k in ['if not q . bind ( s_ , cons ( s . constants [ "S_VALUE" ] ) ) :', 'if not q . bind ( t , conc ( cons ( s . constants [ "PREFIX" ] ) , s_ ) ) :',
          'if not q . bind ( x , conc ( cons ( s . constants [ "PREFIX" ] ) , x ) ) :', 'if not q . bind ( x , y ) :', 'if not q . bind ( y , z ) :',
          'if not q . bind ( z , s . constants [ "Z_VALUE" ] ) :']:
    put("<top>", k, W("P", "the stage's equation, as a binding, and the test that it holds", "METRICS class P (equality); rule 1 (failure changes the report)"))
for k in ['failed . append ( "x = y" )', 'failed . append ( "y = z" )']:
    put("<top>", k, [(0, "P", "record that the stage's equation does not hold", "METRICS rule 1"),
                     (4, "H", "text of the failed equation, for print", HAD),
                     (5, "P", "record that the stage's equation does not hold", "METRICS rule 1")])
for k in ['failed . append ( "conc(%s, s, t)" % show ( cons ( s . constants [ "PREFIX" ] ) ) )', 'failed . append ( "s = %s" % show ( cons ( s . constants [ "S_VALUE" ] ) ) )',
          'failed . append ( "x = %s ++ x" % show ( cons ( s . constants [ "PREFIX" ] ) ) )', 'failed . append ( "z = %s" % show ( s . constants [ "Z_VALUE" ] ) )']:
    put("<top>", k, failed_append_rendered)

# extended P03: query and search
for k in ['query = ( ( conc , ( a , b , cons ( s . constants [ "WHOLE" ] ) ) ) , )',
          'query = ( ( conc , ( a , cons ( s . constants [ "SECOND" ] ) , cons ( s . constants [ "WHOLE" ] ) ) ) , )',
          'query = ( ( conc , ( cons ( s . constants [ "FIRST" ] ) , b , cons ( s . constants [ "WHOLE" ] ) ) ) , )',
          'query = ( ( conc , ( cons ( s . constants [ "FIRST" ] ) , cons ( s . constants [ "SECOND" ] ) , c ) ) , )',
          'query = ( ( rev , ( a , cons ( s . constants [ "BACKWARDS" ] ) ) ) , )',
          'query = ( ( rev , ( cons ( s . constants [ "FORWARDS" ] ) , b ) ) , )']:
    put("<top>", k, W("P", "the query, as a goal list", "METRICS class P (the query); rule 15 for cons"))
put("<top>", 'for _ in search ( query , children , done , trail , stack ) :', W("C", "search directive: depth-first search for every answer", "METRICS class C (search directives)"))

# core P03: queries
put("<top>", 'known [ "b" ] = rev ( s . constants [ "FORWARDS" ] )', W("P", "the query rev(<seq>, b), computed forwards", P3))
put("<top>", 'known [ "c" ] = conc ( s . constants [ "FIRST" ] , s . constants [ "SECOND" ] )', W("P", "the query conc(<seq>, <seq>, c), computed forwards", P3))
for k in ['answers = front ( s . constants [ "SECOND" ] , s . constants [ "WHOLE" ] )', 'answers = rest ( s . constants [ "FIRST" ] , s . constants [ "WHOLE" ] )',
          'answers = split ( s . constants [ "WHOLE" ] )', 'answers = unrev ( s . constants [ "BACKWARDS" ] )']:
    put("<top>", k, W("P", "the query, applied through the direction function", "METRICS class P (the query); the function it calls is R (rule 14)"))
for k in ['for a , b in answers :', 'for a in answers :', 'for b in answers :']:
    put("<top>", k, W("P", "the query asks for every answer: taking each one the generator gives", "METRICS rule 1 (removing it changes the answers reported)"))
for k in ['known [ "a" ] , known [ "b" ] = a , b', 'known [ "a" ] = a', 'known [ "b" ] = b']:
    put("<top>", k, W("H", "collecting an answer already computed into the registered bindings", HAD))

# ---------------------------------------------------------------- functions
def fn(scope, cls, construct, rule, keys):
    for k in keys:
        put(scope, k, W(cls, construct, rule))

# evaluators: equal, plus, times, conc_places (rule 19 split)
EVAL_T = ['if a is not None and b is not None :', 'if a is not None :', 'if b is not None :', 'if c is None :',
          'if a is not None and c is not None :', 'if b is not None and c is not None :', 'return None']
for sc in ["equal", "plus", "times", "conc_places"]:
    fn(sc, "R", "evaluator: test of which places are known / verdict to wait", R19T, EVAL_T)
fn("equal", "P", "evaluator of a = b: computing or testing", R19E, ['def equal ( a , b ) :', 'return ( a , b ) if a == b else False', 'return a , a', 'return b , b'])
fn("plus", "P", "evaluator of a + b = c: computing or testing", R19E, ['def plus ( a , b , c ) :', 'return ( a , b , c ) if a + b == c else False', 'return a , b , a + b', 'return a , c - a , c', 'return c - b , b , c'])
fn("times", "P", "evaluator of a * b = c: computing or testing", R19E, ['def times ( a , b , c ) :', 'if a != 0 :', 'if b != 0 :', 'return ( None , b , c ) if c == 0 else False',
   'return ( a , None , c ) if c == 0 else False', 'return ( a , b , c ) if a * b == c else False', 'return ( a , c // a , c ) if c % a == 0 else False',
   'return ( c // b , b , c ) if c % b == 0 else False', 'return a , b , a * b'])
fn("conc_places", "P", "evaluator of conc(a, b, c): computing c or testing", R19E, ['def conc_places ( a , b , c ) :', 'r = conc ( a , b )', 'return ( a , b , c ) if r == c else False', 'return a , b , r'])

fn("place", "R", "value of a place, None while unknown (holding)", R19H, ['def place ( p ) :', 'return known . get ( p ) if isinstance ( p , str ) else p'])
for k in [l for l in open(os.path.dirname(os.path.abspath(__file__)) + "/keys.txt", encoding="utf-8").read().split("\n") if "('decide'," in l]:
    put("decide", eval(k.split(" ", 1)[1])[1], W("R", "decide: taking up the held relations until none can be decided", R19H))

# conc / rev forwards (P), and extended relations (P)
fn("conc", "P", "conc by its two cases, forwards", P3, ['def conc ( a , b ) :', 'if not a :', 'return ( a [ 0 ] , ) + conc ( a [ 1 : ] , b )', 'return b',
   'return ( a [ 0 ] , conc ( a [ 1 ] , b ) )'])
put("conc", 'a = deref ( a )', W("P", "conc forwards: dereferencing the first place's term", P15))
fn("conc", "P", "conc as a relation: its cases' heads (unification) and bodies", "METRICS class P (definition by cases); rule 15 (unify is S, its calls state the heads)",
   ['def conc ( a , b , c ) :', 'h , a1 , c1 = Var ( "h" ) , Var ( "a1" ) , Var ( "c1" )', 'if unify ( ( a , b ) , ( NIL , c ) ) :',
    'if unify ( ( a , c ) , ( ( h , a1 ) , ( h , c1 ) ) ) :', 'yield ( ( conc , ( a1 , b , c1 ) ) , )', 'yield ( )'])
fn("rev", "P", "rev by its two cases, forwards", P3, ['def rev ( a ) :', 'if not a :', 'return ( )', 'return conc ( rev ( a [ 1 : ] ) , ( a [ 0 ] , ) )'])
fn("rev", "P", "rev as a relation: its cases' heads (unification) and bodies, conjuncts in order", "METRICS class P (definition by cases); rule 15",
   ['def rev ( a , b ) :', 'h , l , q = Var ( "h" ) , Var ( "l" ) , Var ( "q" )', 'if unify ( ( a , b ) , ( NIL , NIL ) ) :', 'if unify ( a , ( h , l ) ) :',
    'yield ( ( rev , ( l , q ) ) , ( conc , ( q , ( h , NIL ) , b ) ) )', 'yield ( )'])
fn("cons", "P", "the sequence encoding: a tuple as cons cells", P15 + " (construction of encoded values)",
   ['def cons ( seq ) :', 'for e in reversed ( seq ) :', 'return t', 't = ( )', 't = ( cons ( e ) if isinstance ( e , tuple ) else e , t )'])

# direction functions (R, rule 14)
fn("split", "R", "conc in its splitting direction (c known)", R14, ['def split ( c ) :', 'for a , b in split ( c [ 1 : ] ) :', 'if c :', 'yield ( ) , c', 'yield ( c [ 0 ] , ) + a , b'])
fn("rest", "R", "conc in the direction a, c known, b computed", R14, ['def rest ( a , c ) :', 'if a and c and a [ 0 ] == c [ 0 ] :', 'if not a :', 'yield c', 'yield from rest ( a [ 1 : ] , c [ 1 : ] )'])
fn("front", "R", "conc in the direction b, c known, a computed", R14, ['def front ( b , c ) :', 'for a in front ( b , c [ 1 : ] ) :', 'if b == c :', 'if c :', 'yield ( )', 'yield ( c [ 0 ] , ) + a'])
fn("unrev", "R", "rev backwards (b known), conc conjunct moved first", R14 + "; rule 4 (one move)", ['def unrev ( r ) :', 'for l in unrev ( q ) :', 'for q , last in split ( r ) :',
   'if len ( last ) == 1 :', 'if not r :', 'yield ( )', 'yield ( last [ 0 ] , ) + l'])

# extended S of the program's own
for k in [l for l in open(os.path.dirname(os.path.abspath(__file__)) + "/keys.txt", encoding="utf-8").read().split("\n") if "('unify'," in l]:
    put("unify", eval(k.split(" ", 1)[1])[1], W("S", "unify: unification of terms (program's own mechanism)", S19))
fn("children", "S", "resolution: children of a goal list", S19, ['( relation , args ) , rest = goals [ 0 ] , goals [ 1 : ]', 'def children ( goals ) :', 'for body in relation ( * args ) :', 'yield body + rest'])
fn("done", "S", "resolution: a goal list is solved when empty", S19, ['def done ( goals ) :', 'return not goals'])

# show: output adapter
for k in [l for l in open(os.path.dirname(os.path.abspath(__file__)) + "/keys.txt", encoding="utf-8").read().split("\n") if "('show'," in l]:
    put("show", eval(k.split(" ", 1)[1])[1], W("H", "show: output adapter rendering a value", HAD))

# stdlib-concurrency: threads
fn("told", "C", "told: waking the waiting relation threads", CTH, ['def told ( ) :', 'changed . notify_all ( )', 'count [ "busy" ] += len ( waiting )', 'count [ "news" ] += 1'])
put("told", 'waiting . clear ( )', W("R", "clearing the record of waiting relations as they are woken", R19H + " (what it records about what waits)"))
fn("pose", "C", "pose: starting a thread for a relation", CTH, ['count [ "busy" ] += 1', 'def pose ( rel ) :', 'threading . Thread ( target = hold , args = ( rel , ) , daemon = True ) . start ( )', 'with changed :'])
fn("settle", "C", "settle: waiting until no relation thread is busy", CTH, ['changed . wait_for ( lambda : count [ "busy" ] == 0 )', 'def settle ( ) :', 'with changed :'])
fn("hold", "R", "hold: a relation's thread deciding it (holding)", R19H, ['def hold ( rel ) :', 'name , places = rel', 'else :', 'failed . append ( rel )',
   'for p , x in zip ( places , outcome ) :', 'if isinstance ( p , str ) and p not in known :', 'if isinstance ( p , str ) and x is not None and p not in known :',
   'if outcome is False :', 'known [ p ] = x', 'waiting . append ( rel )',
   'while ( outcome := EVALUATOR [ name ] ( * [ place ( p ) for p in places ] ) ) is None :',
   'while ( outcome := RELATION [ name ] ( * [ place ( p ) for p in places ] ) ) is None :'])
fn("hold", "C", "hold: synchronisation of the relation thread", CTH, ['changed . notify_all ( )', 'changed . wait_for ( lambda : count [ "news" ] != seen )',
   'count [ "busy" ] -= 1', 'if new :', 'new = False', 'new = True', 'seen = count [ "news" ]', 'told ( )', 'with changed :'])

# extended Relation wrapper (holding, R) with its freeze call (C) and repr (H)
fn("Relation", "R", "Relation: a relation held as a goal of the queue (holding)", R19H, ['class Relation :', 'def __call__ ( self ) :', 'def __init__ ( self , name , evaluate , places ) :',
   'elif outcome is False :', 'else :', 'failed . append ( self )', 'for p , x in zip ( values , outcome ) :', 'if isinstance ( p , Var ) and x is not None :', 'if outcome is None :',
   'outcome = self . evaluate ( * [ None if isinstance ( x , Var ) else x for x in values ] )', 'q . bind ( p , x )',
   'self . name , self . evaluate , self . places = name , evaluate , places', 'values = [ deref ( p ) for p in self . places ]'])
put("Relation", 'q . wait ( self , * [ x for x in values if isinstance ( x , Var ) ] )', W("C", "suspension call q.wait: the goal waits on its unbound unknowns", "METRICS class C (coroutine and freeze calls)"))
fn("Relation", "H", "Relation.__repr__: rendering a held goal for observe()/print", HAD, ['def __repr__ ( self ) :', 'return "%s%r" % ( self . name , tuple ( self . places ) )'])

# ---------------------------------------------------------------- overrides by text group
OV = {}
def ov(group, scope, key, spec):
    OV[(group, scope, key)] = spec
# P03 core (and stdlib-concurrency, same text): the bindings dict only serves observe()
ov("P03-core", "<top>", 'known = { }', W("H", "bindings dict registered for observe()", HAD))
# extended P01: failure bookkeeping is the program's own report of an inconsistent stage
ov("ext-P01", "<top>", 'failed = [ ]', W("P", "the stage's relations found not to hold", "METRICS rule 1"))

def group_of(text):
    conf, f = text.split("/")
    if f.startswith("P03") and conf != "extended": return "P03-core"
    if conf == "extended" and f.startswith("P01"): return "ext-P01"
    return conf

def lookup(text, scope, key):
    g = group_of(text)
    if (g, scope, key) in OV: return OV[(g, scope, key)]
    if (None, scope, key) in T: return T[(None, scope, key)]
    if scope == "<top>" and key.startswith("cp . "):
        return W("H", "harness call " + key.split("(")[0].replace(" ", ""), HCALL + " item 4")
    raise KeyError((text, scope, key))

def carve(toks, cls, construct, rule):
    """Per-token classes for one segment, carving out harness reads."""
    out = [(cls, construct, rule)] * len(toks)
    if cls == "H": return out
    i = 0
    while i < len(toks):
        if toks[i] == "s" and i + 3 < len(toks) and toks[i+1] == "." and toks[i+2] in ("constants", "params") and toks[i+3] == "[":
            j = i + 4; depth = 1
            while depth:
                if toks[j] == "[": depth += 1
                if toks[j] == "]": depth -= 1
                j += 1
            # further subscripts belong to the read: s.params["order"][s.k - 1]
            while j < len(toks) and toks[j] == "[":
                depth = 1; j += 1
                while depth:
                    if toks[j] == "[": depth += 1
                    if toks[j] == "]": depth -= 1
                    j += 1
            a = i - 1 if i > 0 and toks[i-1] == "," else i
            for t in range(a, j): out[t] = H_CONST
            i = j
        else:
            i += 1
    return out

def classify(text):
    src, toks = load(text); sc = scopes(src)
    per = [None] * len(toks)
    bylines = {}
    for idx, ln, tk in toks: bylines.setdefault(ln, []).append(idx)
    prev = None
    for ln in sorted(bylines):
        idxs = bylines[ln]
        body = [i for i in idxs if toks[i][2] not in ("<INDENT>", "<DEDENT>")]
        lead = [i for i in idxs if i not in body]
        for i in lead:
            per[i] = prev  # with the construct before
        if not body:
            continue
        line_toks = [toks[i][2] for i in body]
        key = " ".join(t for t in line_toks if t != "<NEWLINE>")
        spec = lookup(text, sc[ln], key)
        if callable(spec): spec = spec(line_toks)
        bounds = [s[0] for s in spec] + [len(body)]
        for (start, cls, con, rule), end in zip(spec, bounds[1:]):
            seg = body[start:end]
            for i, c in zip(seg, carve([toks[i][2] for i in seg], cls, con, rule)):
                per[i] = c
        prev = per[body[-1]]
    # leading layout before any construct (none expected)
    assert all(p is not None for p in per), text
    spans = []
    for i, c in enumerate(per):
        if spans and (spans[-1]["class"], spans[-1]["construct"], spans[-1]["rule"]) == c and spans[-1]["to"] == i - 1:
            spans[-1]["to"] = i
        else:
            spans.append({"from": i, "to": i, "class": c[0], "construct": c[1], "rule": c[2]})
    return spans, len(toks)

if __name__ == "__main__":
    result, totals = {}, {}
    for t in texts():
        spans, n = classify(t)
        cov = [0] * n
        for s in spans:
            for i in range(s["from"], s["to"] + 1): cov[i] += 1
        assert all(c == 1 for c in cov), t
        result[t] = spans
        tot = {}
        for s in spans: tot[s["class"]] = tot.get(s["class"], 0) + s["to"] - s["from"] + 1
        totals[t] = (n, tot)
    json.dump(result, open(os.path.dirname(os.path.abspath(__file__)) + "/tokens.json", "w"), ensure_ascii=False, indent=0)
    for t, (n, tot) in totals.items():
        print("%-28s %4d  " % (t, n) + "  ".join("%s=%d" % (k, tot.get(k, 0)) for k in "PCRSH"))
