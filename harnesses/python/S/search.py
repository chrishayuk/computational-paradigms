"""S mechanism: backtracking search (depth-first, chronological).

Owns: the trail (a plain list of undo callables) and undo().
Variables: none of its own; a node is whatever the caller says it is.

search(root, children, is_solution, trail=None, stack=None) is a generator.
The tree is given by two functions of the caller:
  is_solution(node) -- true if node is a solution: it is yielded, not expanded;
  children(node)    -- an iterable of node's children, tried in its order
                       (it may be a generator, and is advanced lazily).
Nodes are visited depth first, leftmost child first, root included; after a
subtree is finished, the search returns to the most recent choice point that
has an untried child (chronological backtracking). Solutions are yielded one
at a time, in that order, so a caller takes one (next) or many (a loop); the
search does nothing until asked for the next solution.

Trail. A caller that changes shared state to make a child (binding a
variable, narrowing a domain) appends a zero-argument callable to `trail`
that undoes the change. Before each child of a node is produced, the trail is
undone back to its length when that node was reached, so every child starts
from its parent's state. When the search is exhausted, the trail is undone to
its length at the start. A caller that stops early keeps the state of the
last solution; undo(trail, mark) restores an earlier state.

The search is iterative: its depth is limited by memory, not by the
recursion limit. `stack`, if given, is the list used for the pending choice
points (one entry per open node: its iterator of untried children and its
trail mark), so that a caller can register it as its pending structure.
"""


def undo(trail, mark):
    """Undo the trail's entries after its first `mark`, last first."""
    while len(trail) > mark:
        trail.pop()()


def search(root, children, is_solution, trail=None, stack=None):
    trail = [] if trail is None else trail
    stack = [] if stack is None else stack
    stack.append((iter((root,)), len(trail)))
    while stack:
        alternatives, mark = stack[-1]
        undo(trail, mark)
        node = next(alternatives, stack)  # the stack itself marks "no more"
        if node is stack:
            stack.pop()
        elif is_solution(node):
            yield node
        else:
            stack.append((iter(children(node)), len(trail)))
