#!/usr/bin/env python

import os
import re
import subprocess

from threading import Thread
from time import sleep


def execute(command):
    output = subprocess.check_output(command, shell=True)
    for line in output.decode('utf8').split('\n'):
        yield line


def wait_docker(container_name):
    for i in range(10):
        for line in execute('docker ps'):
            if re.split('\s+', line)[-1] == container_name:
                return
        print(f'{container_name} is not up yet, wait 1 second.')
        sleep(1)

def open_browser_session(container_name):
    wait_docker(container_name)

    print('preparing to open broswer session')
    for line in execute(f'docker exec -it {container_name} jupyter-notebook list'):
        match = re.search(r'token=(?P<token>\w+)', line)
        if match:
            token = match.group('token')
            subprocess.check_call('xdg-open http://localhost:8888/?token={}'.format(token), shell=True)


def start_tensorflow_docker(input_dir='input', notebook_dir='notebooks', docker_name=None):

    def check_directory(mapping_directory):
        if not os.path.exists(mapping_directory):
            os.makedirs(mapping_directory)
        return os.path.abspath(mapping_directory)

    input_dir = check_directory(input_dir)
    notebook_dir = check_directory(notebook_dir)

    if docker_name is None:
        name = os.path.basename(os.getcwd())
        docker_name = re.sub(r'([A-Z])', r'_\g<1>', name).lower().strip('_')

    thread = Thread(target=open_browser_session, args=(docker_name,), daemon=True)
    thread.start()

    os.system(
        f'docker run -p 8888:8888 --runtime=nvidia -v {input_dir}:/input -v{notebook_dir}:/notebooks  --rm --name {docker_name} -it tensorflow-gpu-vim'
    )

if __name__ == '__main__':
    start_tensorflow_docker()
