#!/bin/bash
WU_VERSION="2.06"
declare -i LOWER_BOUND=0
declare -i UPPER_BOUND=9999

for file in ./xoroshigo_configs/*;
do
    STRIPPED_FILENAME=$(basename "$file" .npz)
    FILENAME=$(basename "$file")
    echo "Staging file $file"
    bin/stage_file --verbose --copy "$file"
    #Conf2
    for i in $(seq $LOWER_BOUND $UPPER_BOUND); do
        wu_name="xoroshigo_${WU_VERSION}_${STRIPPED_FILENAME}_${i}"
        echo "create_work: ${wu_name}"
        bin/create_work --appname xoroshigo2 \
            --wu_template templates/xoroshigo_in_"$STRIPPED_FILENAME" \
            --result_template templates/xoroshigo_out \
            --command_line "--passthrough_child \"$FILENAME\" 30000000 $i input.npz" \
            --wu_name "${wu_name}" \
            --min_quorum 2 \
            --credit 5000

    done
done
