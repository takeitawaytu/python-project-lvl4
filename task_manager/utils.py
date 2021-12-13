import json
from os.path import abspath, dirname, join, sep

ABSOLUTE_PATH_FIXTURE_DIR = '{abs_path}{sep}{dir_fixtures}{sep}'.format(
    abs_path=abspath(dirname(__file__)),
    sep=sep,
    dir_fixtures='fixtures',
)


def read_file(path_to_file):
    """
    Read file.
    Args:
        path_to_file: path to file
    Returns:
        any: data from file
    """
    with open(path_to_file) as file_descriptor:
        return file_descriptor.read()


def load_jsonfile_from_fixture(filename: str, add_paths: list = None) -> dict:
    """
    Load json file from fixture directory.
    Args:
        filename: file name
        add_paths: add path into fixture directory
    Returns:
        dict:
    """
    add_paths = add_paths or []
    path = join(ABSOLUTE_PATH_FIXTURE_DIR, *add_paths, filename)
    file_data = read_file(path)
    return json.loads(file_data)
