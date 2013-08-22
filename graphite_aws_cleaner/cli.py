"""Graphite AWS cleaner

Usage:
  graphite-aws-cleaner --pattern <pattern> --storage-dir=<graphite_storage_directory> [--loglevel=<loglevel>]

Options:
  -p --pattern=<pattern>    specify instance name pattern to look for
  -d --storage-dir=<dir>    specify graphite storage directory
  -l --loglevel=<loglevel>  specify log level [default: INFO]
  -h --help                 show this
  -v --version              shows version

"""

import logging

from docopt import docopt

from . import (
    __version__,
    remove_hosts_from_graphite,
    get_running_instances_hostnames)


def main():
    arguments = docopt(__doc__, version=__version__)
    loglevel = arguments['--loglevel']
    name_pattern = arguments['--pattern']
    storage_dir = arguments['--storage-dir']

    logger = logging.getLogger('graphite_cleaner')
    logger.setLevel(getattr(logging, loglevel))
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    hostnames = get_running_instances_hostnames(name_pattern)
    remove_hosts_from_graphite(storage_dir, name_pattern, hostnames)