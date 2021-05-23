import logging
import os

from pygit2 import Repository, discover_repository

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
