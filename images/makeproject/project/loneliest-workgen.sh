#!/bin/bash

for i in {0..262143}; do
wu_name="loneseed_1.00_$i"
  echo "create_work: ${wu_name}"
  bin/create_work --appname loneseed \
    --wu_template templates/loneseed_in \
    --result_template templates/loneseed_out \
    --command_line "--start $((i * 1024)) --end $(((i + 1) * 1024))" \
    --wu_name "${wu_name}" \
    --min_quorum 2 \
    --credit 2500

done
