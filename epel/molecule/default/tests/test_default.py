import os
import pytest
import testinfra.utils.ansible_runner
from ansible.template import Templar
from ansible.parsing.dataloader import DataLoader

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.fixture(scope='module')
def ansible_vars(host):
    """
    Return a dict of the variable defined in the role tested or the inventory.
    Ansible variable precedence is respected.
    """
    defaults_files = "file=../../defaults/main.yml"
    vars_files = "file=../../vars/main.yml"

    host.ansible("setup")
    host.ansible("include_vars", defaults_files)
    host.ansible("include_vars", vars_files)
    all_vars = host.ansible.get_variables()
    all_vars["ansible_play_host_all"] = testinfra_hosts
    templar = Templar(loader=DataLoader(), variables=all_vars)
    return templar.template(all_vars, fail_on_undefined=False)


def test_hosts_file(host):
    f = host.file('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


def test_epel_repo_file(host, ansible_vars):
    epel_repo_file = host.file(ansible_vars['epel_repofile_path'])

    assert epel_repo_file.exists
    assert epel_repo_file.user == 'root'
