#!/bin/bash

for i in {0..2097151}; do
wu_name="repeatdecor_1.00_$i"
  echo "create_work: ${wu_name}"
  bin/create_work --appname repeatdecor \
    --wu_template templates/repeatdecor_in \
    --result_template templates/repeatdecor_out \
    --command_line "--start $((i * 8796093022208)) --end $(((i + 1) * 8796093022208))" \
    --wu_name "${wu_name}" \
    --min_quorum 2 \
    --credit 50000

done
