"""The marked constants block of a Python program (README.md, section 3.1):
found, checked and parsed by the harness, never executed by the program.

    # CONSTANTS BEGIN
    # stage 1
    NAME = <literal>
    # stage 3
    OTHER = <literal>
    # CONSTANTS END

Used by `run` (which delivers stage k's entries with stage k) and `check`.
Neither imports nor executes the program.
"""
import ast
import re

STAGE_RE = re.compile(r"^\s*#\s*stage\s+(\d+)\s*$")


def find(lines):
    """(begin, end) 0-based indexes of the marker lines, None if there is no
    block, or a string saying what is wrong."""
    begins = [i for i, l in enumerate(lines) if l.lstrip().startswith("#") and "CONSTANTS BEGIN" in l]
    ends = [i for i, l in enumerate(lines) if l.lstrip().startswith("#") and "CONSTANTS END" in l]
    if not begins and not ends:
        return None
    if len(begins) != 1 or len(ends) != 1 or ends[0] < begins[0]:
        return "there must be one '# CONSTANTS BEGIN' line followed by one '# CONSTANTS END' line (found %d and %d)" % (len(begins), len(ends))
    return begins[0], ends[0]


def parse(text):
    """Returns (block, constants, errors). block is (begin, end) or None;
    constants is {stage: {name: value}}; errors lists what is wrong."""
    lines = text.splitlines()
    where = find(lines)
    if where is None:
        return None, {}, []
    if isinstance(where, str):
        return None, {}, [where]
    b, e = where
    body = lines[b + 1:e]
    errors = []
    try:
        tree = ast.parse("\n".join(body))
    except SyntaxError as x:
        return where, {}, ["line %d: the constants block does not parse: %s" % (b + 1 + (x.lineno or 0), x.msg)]
    headers = [(i + 1, int(m.group(1))) for i, l in enumerate(body) for m in [STAGE_RE.match(l)] if m]
    consts = {}
    for n in tree.body:
        line = b + 1 + n.lineno     # 1-based line number in the program
        stage = None
        for hl, k in headers:
            if hl < n.lineno:
                stage = k
        if not isinstance(n, ast.Assign) or len(n.targets) != 1 or not isinstance(n.targets[0], ast.Name):
            errors.append("line %d: the constants block may hold only assignments of one literal value to one name" % line)
            continue
        try:
            value = ast.literal_eval(n.value)
        except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
            errors.append("line %d: the value assigned to %s is not a literal" % (line, n.targets[0].id))
            continue
        if stage is None:
            errors.append("line %d: %s comes before any '# stage k' line: every constant is tagged with the stage that first uses it" % (line, n.targets[0].id))
            continue
        if stage < 1:
            errors.append("line %d: stage %d: stages are numbered from 1" % (line, stage))
            continue
        name = n.targets[0].id
        if name in consts.get(stage, {}):
            errors.append("line %d: %s is given twice for stage %d" % (line, name, stage))
            continue
        consts.setdefault(stage, {})[name] = value
    return where, consts, errors


def blanked(text, where):
    """The program's text with the block's lines between the markers made
    empty, so that line numbers are kept and nothing in the block runs."""
    if where is None:
        return text
    lines = text.split("\n")
    b, e = where
    for i in range(b + 1, e):
        lines[i] = ""
    return "\n".join(lines)
