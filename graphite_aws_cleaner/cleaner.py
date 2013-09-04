import boto
import fnmatch
import logging
import os
import shutil


__all__ = [
    'remove_hosts_from_graphite',
    'get_running_instances_hostnames',
    'noop_remove',
]


logger = logging.getLogger('graphite_cleaner')


def remove_hosts_from_graphite(root_dir, match, keep, remove_function=shutil.rmtree):
    all_matched_directories = _find_all_directories(root_dir, match)
    for directory in all_matched_directories:
        _check(directory, keep, remove_function)


def get_running_instances_hostnames(name_pattern):
    running_instances = _get_all_running_instances()
    matched_instances = _get_match_instances(name_pattern, running_instances)
    return map(_get_instance_hostname, matched_instances)


def _find_all_directories(root_dir, match):
    for root, directories, filenames in os.walk(root_dir):
        for directory in directories:
            if fnmatch.fnmatch(directory, match):
                yield os.path.join(root, directory)


def _check(directory, keep, remove_function):
    hosts_matching_directory = (h for h in keep if directory.endswith('-' + h))
    if not any(hosts_matching_directory):
        logger.info("Removing old graphite directory: {}".format(directory))
        remove_function(directory)

def noop_remove(directory):
    # does nothing, just useful for dry-run and debugging
    return

def _get_instance_hostname(instance):
    return instance.id.replace('i-', '')


def _match_instance_name(instance, name_pattern):
    name = instance.tags['Name']
    return fnmatch.fnmatch(name, name_pattern)


def _get_instances_from_reservations(reservations):
    result = []
    for r in reservations:
        result.extend(r.instances)
    return result


def _get_match_instances(name_pattern, instances):
    return (inst for inst in instances if _match_instance_name(inst, name_pattern))


def _get_all_running_instances():
    ec2_conn = boto.connect_ec2()
    running_reservations = ec2_conn.get_all_instances(filters={"instance-state-name": "running"})
    instances = _get_instances_from_reservations(running_reservations)
    return instances
