#!/usr/bin/env python3

import sys
import subprocess
import argparse
import os

CONFIG_RANGE = "0-100000"
CONFIG_DIR = "./xoroshigo_config"
WU_VERSION = "2.09"
LOWER_BOUND = 0
UPPER_BOUND = 9999
BATCH = 0
parser = argparse.ArgumentParser(description="Creatework for xoroshigo2 - single config")
parser.add_argument("-l", "--lowerbound", type=int, default=0, help="Lower bound value")
parser.add_argument("-u", "--upperbound", type=int, default=9999, help="Upper bound value")
parser.add_argument("-c", "--config_dir", help="Path to config file")
parser.add_argument("-v", "--wu_version", default="2.09", help="WU Version for wu_name concat")
parser.add_argument("-r", "--range", default="0-100000", help="Integer range of config files. syntax: lo-hi (aka 0-6, 0-128, etc)")
parser.add_argument("-b", "--batch", default=0, help="Batch number for boinc database, optional.")
args = parser.parse_args()
if(args.wu_version ):
    WU_VERSION = args.wu_version
if(args.lowerbound != LOWER_BOUND):
    LOWER_BOUND = args.lowerbound
if(args.upperbound != UPPER_BOUND):
    UPPER_BOUND = args.upperbound
if(args.config_dir != CONFIG_DIR):
    CONFIG_DIR = args.config_dir
if(args.config_range != CONFIG_RANGE):
    CONFIG_RANGE = args.config_range
CONFIG_LO = int(CONFIG_RANGE.split("-")[0])
CONFIG_HI = int(CONFIG_RANGE.split("-")[1])

for filename in os.listdir(CONFIG_DIR):
    file_path = os.path.join(CONFIG_DIR, filename)
    FILENAME = file_path.split("/")[-1]

    print(f"Staging file {FILENAME}")
    result = subprocess.run(["bin/stage_file", "--verbose", "--copy", file_path])

    if result.returncode != 0:
        print("Staging file failed, proceeding anyway.")

for i in range(LOWER_BOUND, UPPER_BOUND):
    for filename in os.listdir(CONFIG_DIR):
        FILENAME = file_path.split("/")[-1]
        STRIPPED_FILENAME = FILENAME[0:len(FILENAME)-4]
        file_path = os.path.join(CONFIG_DIR, filename)
        if os.path.isfile(file_path):
            if int(FILENAME.split("-")[1]) in range(CONFIG_LO, CONFIG_HI+1):
                print(f"Processing file: {filename}")
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