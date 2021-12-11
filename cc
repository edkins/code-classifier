#!/usr/bin/python3

from pathlib import Path
from time import sleep
import json
import os
import os.path
import re
import signal
import subprocess
import sys

config_dir = f'{Path.home()}/.code-classifier'
config_file = f'{config_dir}/profiles.json'

re_ssh_profile = re.compile(r'[a-zA-Z][-_a-zA-Z0-9]*')

def create_config_file():
    ssh_profile = input('Enter name of ssh profile: ')
    if re_ssh_profile.match(ssh_profile):
        os.makedirs(config_dir, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump({
                'profiles': [
                    {
                        'name': 'default',
                        'default': True,
                        'ssh_profile': ssh_profile
                    }
                ]
            }, f, indent=4)
    else:
        raise Exception('You entered something strange')

def get_ssh_profile():
    with open(config_file) as f:
        data = json.load(f)
    defaults = list(filter(lambda profile: profile.get('default'), data.get('profiles',[])))
    if len(defaults) == 0:
        raise Exception('Need a default profile')
    elif len(defaults) == 1:
        result = defaults[0]['ssh_profile']
        if not re_ssh_profile.match(result):
            raise Exception('Ssh profile is something strange')
        return result
    else:
        raise Exception('Need exactly one default profile')

def do_rsync(ssh_profile):
    print('rsync')
    subprocess.run(['rsync','-r','./requirements.txt','./alembic.ini','./alembic','./src',f'{ssh_profile}:~'])

def do_remote_code_classification(ssh_profile, args):
    print('ssh python3')
    subprocess.run(['ssh', '-t', ssh_profile, 'python3', '-u', 'src/cc.py', *args])

def main():
    if not os.path.exists(config_file):
        create_config_file()
    ssh_profile = get_ssh_profile()
    do_rsync(ssh_profile)
    do_remote_code_classification(ssh_profile, sys.argv[1:])

if __name__ == '__main__':
    main()
