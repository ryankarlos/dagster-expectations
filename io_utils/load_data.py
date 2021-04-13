import requests
import os
import logging
from pygit2 import discover_repository, Repository

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)
LOG.setLevel("DEBUG")
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
DATA_DIR = "../data/"


def get_repo_root() -> Repository:
    """
    Get the repo root independent of current working dir
    Returns
    -------
    Repository
    """
    path = os.getcwd()
    repo_path = discover_repository(path)
    return repo_path.rstrip(".git/")


def get_data_dir_path():
    return os.path.join(get_repo_root(), "data")


def read_csv_from_gh(url, filename, overwrite=False):
    req = requests.get(url, allow_redirects=True)
    filepath = os.path.join(get_data_dir_path(), filename)
    if os.path.exists(filepath) and overwrite is True:
        LOG.info("Found existing file --- so deleting and creating new one")
        with open(filepath, "wb") as f:
            f.write(req.content)
    elif os.path.exists(filepath) and overwrite is False:
        LOG.info(
            "Existing file name already present, if need"
            " to overwrite set the overwite arg to True"
        )
    else:
        LOG.info("File not present, so creating new csv and writing data")
        with open(filepath, "wb") as f:
            f.write(req.content)


if __name__ == "__main__":
    url = "https://github.com/facebook/prophet/blob/master/examples/example_wp_log_peyton_manning.csv"
    filename = "manning.csv"
    x = get_data_dir_path()
    print(x)
    read_csv_from_gh(url, filename, overwrite=True)
