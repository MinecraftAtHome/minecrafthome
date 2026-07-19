#!/bin/bash

for i in {0..65536}; do
wu_name="diaveins2_1.00_$i"
  echo "create_work: ${wu_name}"
  bin/create_work --appname diaveins2 \
    --wu_template templates/diaveins2_in \
    --result_template templates/diaveins2_out \
    --command_line "--start $((i * 4096)) --end $(((i + 1) * 4096))" \
    --wu_name "${wu_name}" \
    --min_quorum 2 \
    --credit 20000

done
