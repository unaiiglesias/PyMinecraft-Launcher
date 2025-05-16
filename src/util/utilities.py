import json
from pathlib import Path
from os import remove

def load_json(filename):
    """
    returns json saved in filename (filename complete path + .json suffix)
    Raises FileNotFoundError if the file is not found
    """
    with open(filename, "r", encoding="utf-8") as json_file:
        return json.load(json_file)

def save_json(content, filename):
    """
    writes contents to filename.
    filename has to be complete path to file.json
    """
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(content, file, indent=4)

def get_default_path():
    user_path = str(Path.home())
    installation_path = user_path + "\\AppData\\Roaming\\.minecraft"
    return installation_path

def check_if_path_is_valid(path):
    """
    Chekc if the given path is accessible (can be read and written)
    AKA: The app's got permission to access it

    Returns:
        True if path accessible, False othersie
    """
    try:
        test_file_path = path + "\\test.txt"
        with open(test_file_path, "w") as test_file:
            test_file.write("Do we got permission?")
        remove(test_file_path)
        return True
    except (PermissionError, FileNotFoundError):
        return False
