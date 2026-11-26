#!/usr/bin/env bash
# Run the SWI-Prolog measurement-qualification probes and print one line
# per result:
#
#   CLASS|probe[variant]|key=value
#
# CLASS is I (expected to be identical on every platform for the same
# SWI-Prolog version and flags) or D (expected to depend on platform,
# build, memory layout or sampling phase). Any output line a probe prints
# without a label (a warning on stderr, for instance) is kept as
# D|probe[variant]|unlabelled=<line>. Each run also reports its exit status.
#
# Usage: probes/run.sh > output.txt        (SWIPL=/path/to/swipl to override)
set -u
SWIPL=${SWIPL:-swipl}
cd "$(dirname "$0")" || exit 2

label() {   # $1 = probe[variant]; reads probe output on stdin
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      I\|*|D\|*) printf '%s|%s|%s\n' "${line%%|*}" "$1" "${line#*|}" ;;
      '') ;;
      *) printf 'D|%s|unlabelled=%s\n' "$1" "$line" ;;
    esac
  done
}

# run NAME VARIANT FILE GOAL [extra swipl options...]
run() {
  local name=$1 variant=$2 file=$3 goal=$4; shift 4
  local tag="$name[$variant]" status
  "$SWIPL" "$@" -f none -q -g "$goal" -t halt "$file" </dev/null 2>&1 | label "$tag"
  status=${PIPESTATUS[0]}
  printf 'I|%s|exit=%s\n' "$tag" "$status"
}

"$SWIPL" --version 2>&1 | label 'run[version]'

run choicepoints main     choicepoints.pl main

run stacks gc_on          stacks.pl 'main(gc(on))'
run stacks gc_off         stacks.pl 'main(gc(off))'
run stacks gc_off_then_gc stacks.pl 'main(gc(off_then_gc))'
run stacks alloc          stacks.pl 'main(alloc)'
run stacks keys           stacks.pl 'main(keys)'

run heartbeat patterns    heartbeat.pl 'main(patterns)'
run heartbeat sampled     heartbeat.pl 'main(sampled)'
for k in 0 1 7 300; do
  run heartbeat "phase$k" heartbeat.pl "main(phase($k))"
done

run tables usage          tables.pl 'main(usage)'
run tables limit          tables.pl 'main(limit)'

run attvars counts        attvars.pl 'main(counts)'
run attvars residue       attvars.pl 'main(residue)'

run inferences plain      inferences.pl 'main(plain)'
run inferences optimise   inferences.pl 'main(optimise)' -O
run inferences debug      inferences.pl 'main(debug)'

run hazard plain          hazard.pl 'main(plain)'
run hazard debug          hazard.pl 'main(debug)'

run engines main          engines.pl main
run process main          process.pl main

# Toplevel overhead: two queries piped into the interactive toplevel.
{
  printf '%s\n' 'statistics(inferences, A), nb_setval(tl_a, A), fail.'
  printf '%s\n' 'nb_getval(tl_a, A), statistics(inferences, B), D is B-A, format("D|between_queries=~d~n", [D]), fail.'
} | "$SWIPL" -f none -q toplevel.pl 2>&1 | grep -v '^false\.$' | label 'toplevel[main]'
printf 'I|toplevel[main]|exit=%s\n' "${PIPESTATUS[1]}"
