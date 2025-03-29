#!/bin/bash

for i in {0..10000}; do
    wu_name="xoroshigo_1.04_config-001-hixorlo-fullinfo-rank100_$i"
    echo "create_work: ${wu_name}"
    bin/create_work --appname xoroshigo \
        --wu_template templates/xoroshigo_in \
        --result_template templates/xoroshigo_out \
        --command_line "--device \"0 config-001-hixorlo-fullinfo-rank100.npz 1500000 $i input.npz\"" \
        --wu_name "${wu_name}" \
        --min_quorum 2 \
        --credit 2500 \
    config-001-hixorlo-fullinfo-rank100.npz 

done