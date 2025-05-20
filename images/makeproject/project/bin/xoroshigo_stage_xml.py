#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import sys
import argparse
import os



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
    




parser = argparse.ArgumentParser(description="Creatework for xoroshigo2 - single config")
parser.add_argument("-c", "--config_dir", default="xoroshigo_configs", help="Path to config file")
parser.add_argument("-r", "--range", default="0-0", help="Integer range of config files. syntax: lo-hi (aka 0-6, 0-128, etc)")
args = parser.parse_args()
CONFIG_DIR = args.config_dir
CONFIG_RANGE = args.range
CONFIG_LO = int(CONFIG_RANGE.split("-")[0])
CONFIG_HI = int(CONFIG_RANGE.split("-")[1])
if(CONFIG_HI == 0 and CONFIG_LO == 0):
    CONFIG_HI = -1
    

for filename in os.listdir(CONFIG_DIR):
    file_path = os.path.join(CONFIG_DIR, filename)
    if os.path.isfile(file_path):
        print(f"Processing file: {filename}")
        FILENAME = file_path.split("/")[-1]
        STRIPPED_FILENAME = FILENAME[0:len(FILENAME)-4]
        if int(FILENAME.split("-")[1]) in range(CONFIG_LO, CONFIG_HI+1) or CONFIG_HI == -1:
                xml_file = "templates/xoroshigo_in_TEMPLATE"
                output_file = f"templates/xoroshigo_in_{STRIPPED_FILENAME}"
                
                replace_physical_name(xml_file, STRIPPED_FILENAME, output_file)