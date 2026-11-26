#!/bin/sh
# Run the measurement-qualification probes.
#   ./run.sh                 run every probe with python3
#   ./run.sh PY1 PY2 ...     run every probe with each interpreter given
# Output for each interpreter goes to stdout and to out/<version>.txt.
# The probes are run with -E (ignore PYTHON* variables) and -s (no user
# site-packages); PYTHONHASHSEED is set explicitly where it matters.
set -u
cd "$(dirname "$0")"
mkdir -p out
[ $# -eq 0 ] && set -- python3
for PY in "$@"; do
  V=$("$PY" -c 'import sys; print(sys.version.split()[0])')
  {
    echo "=== $PY ($V) on $(uname -sm)"
    for P in p1_instructions p1b_first_call p1d_cost p2_algops p3_memory \
             p4_retained p5_recursion p6_budget; do
      echo "--- $P"
      PYTHONHASHSEED=0 "$PY" -s "$P.py"
    done
    echo "--- p1c_determinism (PYTHONHASHSEED 0, 0, 1, 2, random, random)"
    for S in 0 0 1 2; do PYTHONHASHSEED=$S "$PY" -s p1c_determinism.py; done
    for S in 1 2; do "$PY" -E -s p1c_determinism.py; done
  } 2>&1 | tee "out/$V.txt"
done
