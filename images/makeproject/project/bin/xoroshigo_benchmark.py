#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import sys
import argparse
import os
import subprocess
import time
import shutil
import platform
import csv
import concurrent.futures

def replace_physical_name(xml_file, new_name, output_file):
    """
    Replace 'REPLACE_ME' in the physical_name element with a new name and save to output file.
    
    Args:
        xml_file (str): Path to the input XML file
        new_name (str): The new name to replace 'REPLACE_ME' with
        output_file (str): Path to save the modified XML
    """
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Find the physical_name element
    physical_name_elem = root.find(".//physical_name")
    
    if physical_name_elem is not None and physical_name_elem.text == "REPLACE_ME":
        physical_name_elem.text = new_name
        print(f"Replaced 'REPLACE_ME' with '{new_name}'")
    else:
        print("Warning: Could not find 'REPLACE_ME' in physical_name element")
    
    # Write the modified XML to the output file
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"Modified XML saved to '{output_file}'")

def delete_file(path):
     if os.path.exists(path):
        os.remove(path)

def get_config_performance(config_path, iterations, prng, binary_path, work_dir, baseline_run, baseline_iter):
    CONFNAME = config_path.split("/")[-1]
    STRIPPED_CONFNAME = CONFNAME[0:len(CONFNAME)-4]
    BINNAME = binary_path.split("/")[-1]

    cmd = [f"./{BINNAME}",f"./{CONFNAME}", iterations, prng, CONFNAME]
    try:
        if(os.path.exists(work_dir) == 0):
            os.makedirs(work_dir)

        shutil.copy(config_path, work_dir)
        shutil.copy(binary_path, work_dir)

        start_time = time.time()

        result = subprocess.run(cmd, text=True, cwd=work_dir, stdout=subprocess.DEVNULL)

        end_time = time.time()

        runtime = end_time - start_time

        delete_file(f"{work_dir}/checkpoint.npz")
        delete_file(f"{work_dir}/boinc_frac")
        delete_file(f"{work_dir}/boinc_finish_called")
        delete_file(f"{work_dir}/{CONFNAME}")
        if(result.returncode != 0):
            print(f"Baseline failed: {result}")
            delete_file(f"{work_dir}/checkpoint.npz")
            delete_file(f"{work_dir}/boinc_frac")
            delete_file(f"{work_dir}/boinc_finish_called")
            delete_file(f"{work_dir}/{CONFNAME}")
            return -2
        if(baseline_iter != -1):    
            input_path = f'{work_dir}/output.txt'
            with open(input_path) as input_file:
                input_str = input_file.read()
                input_lines = input_str.splitlines()
                iter_count = input_lines[3].split(' ')[1]
                time_per_iter = runtime/int(iter_count)
                line = [STRIPPED_CONFNAME,runtime,baseline_run/runtime,iter_count,time_per_iter,baseline_iter/time_per_iter]
                return line
        else:
            return runtime
    except Exception as e:
        print(f"Exception hit {e}")
        delete_file(f"{work_dir}/checkpoint.npz")
        delete_file(f"{work_dir}/boinc_frac")
        delete_file(f"{work_dir}/boinc_finish_called")
        delete_file(f"{work_dir}/{CONFNAME}")
        return -1


def get_platform_triple(system, arch):
    """
        Given system (Linux, Windows), and arch (AMD64, x86_64, aarch64, ARM64) determine the triple to use
        Example:

        system = Linux, arch = x86_64, triple = x86_64-pc-linux-gnu__lin-modern
        system = Linux, arch = aarch64, triple = aarch64-unknown-linux-gnu__lin-modern
        system = Windows, arch = x86_64, triple = windows_x86_64__win-modern
    """
    triple = ""
    if(system == 'Linux'):
        if(arch == 'x86_64' or arch == 'AMD64'):
            triple += 'x86_64-pc-'
        elif(arch == 'aarch64' or arch == 'ARM64'):
            triple += 'aarch64-unknown-'
        triple += 'linux-gnu__lin-modern'
    elif(system == 'Windows'):
        triple = 'windows_x86_64__win-modern'
    return triple

def get_latest_app_version(app_dir):
    max_ver = 0
    max_ver_string = ""
    for app_ver in os.listdir(app_dir):
        version_parts = app_ver.split('.')
        version_int = int(version_parts[0]) * 100 + int(version_parts[1])
        if(version_int > max_ver):
            max_ver = version_int
            max_ver_string = app_ver
    return max_ver_string

def get_latest_app_version_dir(app_dir):
    max_ver = 0
    max_ver_string = ""
    for app_ver in os.listdir(app_dir):
        version_parts = app_ver.split('.')
        version_int = int(version_parts[0]) * 100 + int(version_parts[1])
        if(version_int > max_ver):
            max_ver = version_int
            max_ver_string = app_ver
    return f"{app_dir}/{max_ver_string}"

def get_binary_path(app_ver_dir, triple):
    """
        Given app_ver_dir, and a platform triple, return a binary path.
        Examples:
        app_ver_dir = apps/xoroshigo2/1.04
        triple = x86_64-pc-linux-gnu__lin-modern
        return apps/xoroshigo2/1.04/x86_64-pc-linux-gnu__lin-modern/xoroshigo2_client_1.04_x86_64-pc-linux-gnu__lin-modern.bin
    """
    app_ver = app_ver_dir.split('/')[-1]
    if(platform.uname().system == 'Linux'):
        return f"{app_ver_dir}/{triple}/xoroshigo2_client_{app_ver}_{triple}.bin"
    elif(platform.uname().system == 'Windows'):
        return f"{app_ver_dir}/{triple}/xoroshigo2_client_{app_ver}_{triple}.exe"
    return "no-plat-found"




parser = argparse.ArgumentParser(description="Creatework for xoroshigo2 - single config")
parser.add_argument("-c", "--config_dir", default="xoroshigo_configs", help="Path to config file")
parser.add_argument("-r", "--range", default="0-0", help="Integer range of config files. syntax: lo-hi (aka 0-6, 0-128, etc)")
parser.add_argument("-b", "--benchmark", default="0", help="Iteration count for benchmarking.")
args = parser.parse_args()
CONFIG_DIR = args.config_dir
CONFIG_RANGE = args.range
CONFIG_LO = int(CONFIG_RANGE.split("-")[0])
CONFIG_HI = int(CONFIG_RANGE.split("-")[1])
CONFIG_ITER = f"{args.benchmark}"

if(CONFIG_HI == 0 and CONFIG_LO == 0):
    CONFIG_HI = -1

if(CONFIG_ITER > 0):
    #Get Triple
    triple = get_platform_triple(platform.uname().system, platform.uname().machine)
    #Get Binary
    bin_path = get_binary_path(get_latest_app_version_dir("apps/xoroshigo2"), triple)
    #Get Baseline
    baseline_run = get_config_performance("xoroshigo_configs/sweep001/config-001-hixorlo-fullinfo-rank100-genfix.npz", CONFIG_ITER, "0", bin_path, "./xoroshigo_conf_test", -1, -1)
    input_path = 'xoroshigo_conf_test/output.txt'

    with open(input_path) as input_file:
        input_str = input_file.read()
        input_lines = input_str.splitlines()
        baseline_iter_count = input_lines[3].split(' ')[1]
        baseline_iter = baseline_run/int(baseline_iter_count)

    with open('benchmark.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        print(f"Baseline: config-001-hixorlo-fullinfo-rank100-genfix.npz, br:{baseline_run}, bri:{baseline_iter_count}, br/bri:{baseline_iter}")
        print(f"{'Config Name':40} {'r':8} {'br/r':7} {'i':8} {'t/i':22} {'(bt/bi)/(t/i)':22}")
        spamwriter.writerow(["Config Name", "Runtime", "Base Runtime/Runtime", "Iteration Count", "Time per iter", "Baseitertime mult"])
        
        # Create the executor and futures list outside the submission loop
        futures = []
        t_num = 0
        
        # Submit all tasks first
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            for filename in sorted(os.listdir(CONFIG_DIR)):
                file_path = os.path.join(CONFIG_DIR, filename)
                if os.path.isfile(file_path):
                    FILENAME = file_path.split("/")[-1]
                    STRIPPED_FILENAME = FILENAME[0:len(FILENAME)-4]
                    if int(FILENAME.split("-")[1]) in range(CONFIG_LO, CONFIG_HI+1) or CONFIG_HI == -1:
                        futures.append(executor.submit(get_config_performance, file_path, CONFIG_ITER, "0", bin_path, f"./xoroshigo_conf_test{t_num}", baseline_run, baseline_iter))
                        t_num += 1
            
            # Process results as they complete
            pool_len = len(futures)
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                completed += 1
                result = future.result()
                spamwriter.writerow(result)
                print(f"{completed/pool_len:.2f} {completed}/{pool_len}")
                # Force flush to see output immediately
                sys.stdout.flush()
else:
    for filename in os.listdir(CONFIG_DIR):
        file_path = os.path.join(CONFIG_DIR, filename)
        if os.path.isfile(file_path):
            print(f"Processing file: {filename}")
            FILENAME = file_path.split("/")[-1]
            STRIPPED_FILENAME = FILENAME[0:len(FILENAME)-4]
            if int(FILENAME.split("-")[1]) in range(CONFIG_LO, CONFIG_HI+1) or CONFIG_HI == -1:
                    xml_file = "templates/xoroshigo_in_TEMPLATE"
                    output_file = f"templates/xoroshigo_in_{STRIPPED_FILENAME}"
                    
                    replace_physical_name(xml_file, FILENAME, output_file)

#single threaded benchmark code
# with open('benchmark.csv', 'w', newline='') as csvfile:
#     with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
#         futures = []
#         spamwriter = csv.writer(csvfile, delimiter=',',
#             quotechar='|', quoting=csv.QUOTE_MINIMAL)
#         print(f"Baseline: config-001-hixorlo-fullinfo-rank100-genfix.npz, br:{baseline_run}, bri:{baseline_iter_count}, br/bri:{baseline_iter}")
#         print(f"{"Config Name":40} {"r":8} {"br/r":7} {"i":8} {"t/i":22} {"(bt/bi)/(t/i)":22}")
#         spamwriter.writerow(["Config Name", "Runtime", "Base Runtime/Runtime", "Iteration Count", "Time per iter", "Baseitertime mult"])
#         for filename in sorted(os.listdir(CONFIG_DIR)):
#             file_path = os.path.join(CONFIG_DIR, filename)
#             if os.path.isfile(file_path):
#                 #print(f"Processing file: {filename}")
#                 FILENAME = file_path.split("/")[-1]
#                 STRIPPED_FILENAME = FILENAME[0:len(FILENAME)-4]
#                 if int(FILENAME.split("-")[1]) in range(CONFIG_LO, CONFIG_HI+1) or CONFIG_HI == -1:
#                         #xml_file = "templates/xoroshigo_in_TEMPLATE"
#                         #output_file = f"templates/xoroshigo_in_{STRIPPED_FILENAME}"
                        
#                         #replace_physical_name(xml_file, FILENAME, output_file)


#                         futures.append(executor.submit(get_config_performance, file_path, CONFIG_ITER, "0", bin_path, f"./xoroshigo_conf_test{t_num}", baseline_run, baseline_iter))
#                         t_num += 1
#                         #run = get_config_performance(file_path, CONFIG_ITER, "0", bin_path, f"./xoroshigo_conf_test{len(threads)}")

#         t_num = 0
#         pool_len = len(futures)
#         for future in concurrent.futures.as_completed(futures):
#             t_num += 1
#             spamwriter.writerow(future.result())
#             print(f"{t_num/pool_len:.2f} {tnum}/{pool_len}")
