#!/bin/sh
# Rerun the whole qualification in the pinned image, from the host, and
# write its output to harnesses/swi-prolog/qualification/output.txt.
# Usage: harnesses/swi-prolog/qualification/rerun.sh   (from the repository root)
repo=$(cd "$(dirname "$0")/../../.." && pwd)
container run --rm --platform linux/amd64 --volume "$repo:/work" --workdir /work \
  ${CP_IMAGE_DIGEST:+-e CP_IMAGE_DIGEST=$CP_IMAGE_DIGEST} \
  cp-agent-swi-prolog:spec-1.0 python3 harnesses/swi-prolog/qualification/run.py \
  > "$repo/harnesses/swi-prolog/qualification/output.txt" 2>&1
status=$?
tail -n 5 "$repo/harnesses/swi-prolog/qualification/output.txt"
exit $status
