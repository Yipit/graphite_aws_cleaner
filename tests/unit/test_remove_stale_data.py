import os
import os.path
import tempfile
from mock import patch, call

from graphite_aws_cleaner import (
    remove_hosts_from_graphite,
    get_running_instances_hostnames,
    noop_remove,
)
from moto import mock_ec2
from moto.ec2 import ec2_backend
import boto


tmpdir = tempfile.mkdtemp(prefix='tests-graphite')


def test_remove_stale_data_from_graphite():
    reset_tmpdir()
    current_hosts = ['server-1', 'server-2', 'server-3']
    old_hosts = ['server-4', 'server-5']
    create_stats('server', instance_id='1')
    create_stats('server', instance_id='2')
    create_stats('server', instance_id='3')
    create_stats('server', instance_id='4')
    create_stats('server', instance_id='5')

    remove_hosts_from_graphite(
        '{tmpdir}/graphite/storage'.format(tmpdir=tmpdir),
        match='*server*',
        keep='1 2 3'.split())

    stored_hosts = list_hosts_with_stored_data()
    assert stored_hosts == current_hosts


@patch('graphite_aws_cleaner.cleaner.logger')
def test_remove_hosts_from_graphite_should_log_dirs_removed(logger):
    reset_tmpdir()
    current_hosts = ['server-1', 'server-2', 'server-3']
    old_hosts = ['server-4', 'server-5']
    create_stats('server', instance_id='1')
    create_stats('server', instance_id='2')
    create_stats('server', instance_id='3')

    expected_deleted_paths = [
        create_stats('server', instance_id='4'),
        create_stats('server', instance_id='5'),
    ]

    remove_hosts_from_graphite(
        '{tmpdir}/graphite/storage'.format(tmpdir=tmpdir),
        match='*server*',
        keep='1 2 3'.split())

    expected_calls = [
        call.info('Removing old graphite directory: {}'.format(expected_deleted_paths[0])),
        call.info('Removing old graphite directory: {}'.format(expected_deleted_paths[1]))
    ]

    logger.info.assert_has_calls(expected_calls)


@patch('graphite_aws_cleaner.cleaner.logger')
def test_should_be_possible_to_specify_remove_function(logger):
    reset_tmpdir()
    current_hosts = ['server-1']
    old_hosts = ['server-2']
    create_stats('server', instance_id='1')

    expected_deleted_paths = [
        create_stats('server', instance_id='2'),
    ]

    remove_hosts_from_graphite(
        '{tmpdir}/graphite/storage'.format(tmpdir=tmpdir),
        match='*server*',
        keep=['1'],
        remove_function=noop_remove)

    expected_logger_calls = [
        call.info('Removing old graphite directory: {}'.format(expected_deleted_paths[0]))
    ]

    logger.info.assert_has_calls(expected_logger_calls)
    assert list_hosts_with_stored_data() == 'server-1 server-2'.split()


@mock_ec2
def test_find_running_aws_machines_by_pattern():
    id1 = create_instance('web_i1')
    id2 = create_instance('web_i2')
    id3 = create_instance('web_i3')
    id4 = create_instance('worker_i3')
    terminate_instance(id1)
    terminate_instance(id2)

    instances = get_running_instances_hostnames('*web*')

    hostname_id3 = id3.replace('i-', '')
    assert len(instances) == 1
    assert instances == [hostname_id3]


def create_file(path, fname):
    with open(os.path.join(path, fname), "w") as f:
        f.write("TEST FILE")


def create_stats(role, instance_id):
    # TODO:
    # add stats to stats_count
    #
    path = '{tmpdir}/graphite/storage/whisper/stats/timers/nginx-api/{role}-{id}'.format(
        tmpdir=tmpdir,
        role=role,
        id=instance_id)
    os.makedirs(path)
    create_file(path, 'count.wsp')
    create_file(path, 'mean.wsp')
    create_file(path, 'upper_90.wsp')
    create_file(path, 'upper.wsp')
    return path


def list_hosts_with_stored_data():
    whisper_path = '{tmpdir}/graphite/storage/whisper/stats/timers/nginx-api'.format(tmpdir=tmpdir)
    return os.listdir(whisper_path)


def create_instance(instance_name):
    ec2_conn = boto.connect_ec2()
    reservation = ec2_conn.run_instances('ami-1234abcd')
    instance = reservation.instances[0]
    instance.add_tag("Name", instance_name)

    # hacky solution for changing instance state name via moto
    ec2_backend.get_instance(instance.id)._state.name = "running"

    return instance.id


def terminate_instance(instance_id):
    ec2_conn = boto.connect_ec2()
    ec2_conn.stop_instances([instance_id])


def reset_tmpdir():
    global tmpdir
    tmpdir = tempfile.mkdtemp(prefix='tests-graphite')

