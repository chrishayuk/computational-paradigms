#!/bin/bash
# One job of a batch, from batch 1C on: SYSTEM CONFIGURATION PROBLEM CHECKOUT
#
#   tools/run-job.sh absys absys P09 ~/cp-roles/run-1C
#
# CHECKOUT is a clone of the public repository at the batch's one commit.
# It is mounted read-only at /work, and only its results/ folder is
# writable, so no job can change the harness or a program while the batch
# runs. Each job writes its own log, results/SYSTEM/logs/BATCH-CONFIGURATION-PROBLEM.tsv,
# so parallel jobs never share a log file.
set -u
sys=$1 cfg=$2 p=$3 co=$4 batch=${BATCH:-1C}
mem=4g
case $sys in
  absys)      img=cp-agent-systems:spec-1.0-m2; env=()     # absys-measure 8a0eefd (PINS.md)
              [ "$p" = P12 ] && mem=16g ;;                   # P12: the large alternative space
  algol-60)   img=cp-agent-systems:spec-1.0; env=() ;;
  swi-prolog) img=cp-agent-swi-prolog:spec-1.0; env=(-e HARNESS_IMAGE_DIGEST=sha256:b51af487f3306fe240eae8c13159c85b5526509952e1b949cc22f48a1f82a742) ;;
  python)     img=cp-agent-python:spec-1.0; env=(-e HARNESS_IMAGE_DIGEST=sha256:fe841081ec55481496a4ab25e538833741295d57d2abdec8d38d74d65fb4715b) ;;
esac
log=results/$sys/logs/$batch-$cfg-$p.tsv
mkdir -p "$co/results/$sys/logs"
container run --rm --platform linux/amd64 --cpus 2 --memory $mem \
  --mount type=bind,source="$co",target=/work,readonly --volume "$co/results":/work/results \
  --workdir /work "${env[@]}" $img \
  python3 tools/run-batch.py $sys $p --configs $cfg --skip-logged --log $log
