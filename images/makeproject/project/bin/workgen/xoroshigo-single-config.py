#!/usr/bin/env python3

import sys
import subprocess
import argparse

WU_VERSION="2.07"
LOWER_BOUND=0
UPPER_BOUND=9999
config_filepath = "xoroshigo_configs/config-001-hixorlo-fullinfo-rank100-genfix.npz"
FILENAME = config_filepath.split("/")[-1]
STRIPPED_FILENAME = FILENAME[0:len(FILENAME)-4]

parser = argparse.ArgumentParser(description="Creatework for xoroshigo2 - single config")
parser.add_argument("-l", "--lowerbound", type=int, help="Lower bound value")
parser.add_argument("-u", "--upperbound", type=int, help="Upper bound value")
parser.add_argument("-c", "--config", help="Path to config file")
parser.add_argument("-v", "--wu_version", help="WU Version for wu_name concat")
args = parser.parse_args()
LOWER_BOUND = args.lowerbound
UPPER_BOUND = args.upperbound
config_filepath = args.config

print(f"Staging file {FILENAME}")
result = subprocess.run(["bin/stage_file", "--verbose", "--copy", config_filepath])

if result.returncode != 0:
    print("Staging file failed")
    exit(1)

for i in range(LOWER_BOUND, UPPER_BOUND):
    wu_name=f"xoroshigo_{WU_VERSION}_{STRIPPED_FILENAME}_{i}"
    print(f"create_work: {wu_name}")
    cmd = [
        "bin/create_work",
        "--appname", "xoroshigo2",
        "--wu_template", f"templates/xoroshigo_in_{STRIPPED_FILENAME}",
        "--result_template", "templates/xoroshigo_out",
        "--command_line", f"--passthrough_child {FILENAME} 30000000 {i} input.npz",
        "--wu_name", wu_name,
        "--min_quorum", "2",
        "--credit", "5000"
    ]
    result = subprocess.run(cmd, text=True)
    if(result.returncode != 0):
        print(f"Create_work failed: {result}")
        exit(1)