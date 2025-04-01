import xml.etree.ElementTree as ET
import os
import re
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def check_version(xml_filepath):
    """
    Parses an XML file, extracts version numbers from <physical_name> tags,
    and compares it to the parent directory name.

    Args:
    xml_filepath (str): The path to the XML file.

        Returns:
    str: The filepath of the XML if the version in the XML does not match the parent
    directory name, otherwise None.
    """
    version_number = ""
    try:
        tree = ET.parse(xml_filepath)
        root = tree.getroot()

        # Extract version from the directory name
        directory = os.path.dirname(xml_filepath)
        logging.debug(f"FullPath: {directory}")
        directory_name = os.path.basename(directory)
        logging.debug(f"Dir name: {directory_name}")
        parent_directory = os.path.dirname(directory)  # Get the parent directory
        logging.debug(f"Parent FullPath: {parent_directory}")
        parent_directory_name = os.path.basename(parent_directory)
        logging.debug(f"Parent Dir Name: {parent_directory_name}")        
        # Find all physical_name elements and extract version numbers
        for physical_name_element in root.findall(".//physical_name"):
            physical_name = physical_name_element.text
            logging.debug(f"Physical Name: {physical_name}")
            # Use regex to find version number (e.g., 1.01, 2.3)
            match = re.search(r"(?<![0-9.])(\d+\.\d{2,3})(?![0-9])", physical_name)
            if match:
                version_number = match.group(1)
                logging.debug(f"Version Number: {version_number}")
            # Compare the extracted version number with the directory name
            if version_number != parent_directory_name:
                logging.error(f"Version Number Mismatch. Version.xml: {version_number} Parent dir: {parent_directory_name}")
                return xml_filepath
            else:
                return None
  
    except ET.ParseError:
        print(f"Error: Could not parse XML file: {xml_filepath}")
        return None
    except FileNotFoundError:
        print(f"Error: File not found: {xml_filepath}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
 
def crawl(directory):
    """

    """
    failed_files = []
    logging.debug(f"Starting search in directory: {directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            if file == "version.xml":
                filepath = os.path.join(root, file)
                logging.debug(f"Found version.xml file: {filepath}")
                if check_version(filepath):
                    logging.info(f"File {filepath} does not match parent version.")
                    failed_files.append(filepath)
                else:
                    logging.debug(f"File {filepath} matches parent version.")

    return failed_files
 # Example Usage:
if __name__ == "__main__":
    xml_file = os.environ["DIRECTORY_TO_CHECK"]  # Replace with the actual path to your XML file
    result = []
    result = (crawl(xml_file))

    if len(result) > 0:
        for file in result:
            print(f" - {file}")
    else:
        print("Success: All version.xml files look correct.")
