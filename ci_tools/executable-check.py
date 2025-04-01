import os
import stat
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def check_executable_permission(filepath):
    """
    Checks if a file has executable permissions for any user.
    """
    try:
        st = os.stat(filepath)
        logging.debug(f"File mode for {filepath}: {st.st_mode:o}")  # Octal representation
        executable_permissions = st.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        has_executable_permission = executable_permissions != 0
        logging.debug(f"Executable bits: {executable_permissions:o}")
        logging.debug(f"File {filepath} has executable permission: {has_executable_permission}")
        return has_executable_permission
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return False  # Treat as not having executable permission
    except Exception as e:
        logging.error(f"Error checking permissions for {filepath}: {e}")
        return False


def find_bin_files_and_check_executable(directory):
    """
    Recursively searches a directory for '.bin' files and checks if they
    have executable permissions.  Returns the filepath of the first .bin
    file found *without* executable permissions.


    Returns:
    - The filepath of a .bin file without executable permission (failure).
    - None if all .bin files have executable permission (success) or if no
    .bin files are found.
    """
    failed_files = []
    logging.debug(f"Starting search in directory: {directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".bin"):
                filepath = os.path.join(root, file)
                logging.debug(f"Found .bin file: {filepath}")
                if not check_executable_permission(filepath):
                    logging.info(f"File {filepath} does not have executable permission.")
                    failed_files.append(filepath)
                else:
                    logging.debug(f"File {filepath} has executable permission.")

    return failed_files  # All .bin files have executable permission, or no .bin files

# Example usage:
if __name__ == "__main__":
    directory_to_search = os.environ["DIRECTORY_TO_CHECK"]  # Replace with your directory
    result = []
    result = (find_bin_files_and_check_executable(directory_to_search))
 

    if len(result) > 0:
        for file in result:
            print(f" - {file}")
    else:
        print("Success: All .bin files have executable permission.")
