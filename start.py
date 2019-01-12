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
        sleep(1)

def open_browser_session(container_name):
    wait_docker(container_name)

    for line in execute(f'docker exec -it {container_name} jupyter-notebook list'):
        match = re.search(r'token=(?P<token>\w+)', line)
        if match:
            token = match.group('token')
            subprocess.check_call('xdg-open http://localhost:8888/?token={}'.format(token), shell=True)


def start_tensorflow_docker(mapping_directory='notebooks', docker_name=None):
    if not os.path.exists(mapping_directory):
        os.makedirs(mapping_directory)
    else:
        mapping_directory = os.path.abspath(mapping_directory)

    if docker_name is None:
        name = os.path.basename(os.getcwd())
        docker_name = re.sub(r'([A-Z])', r'_\g<1>', name).lower().strip('_')

    thread = Thread(target=open_browser_session, args=(docker_name,), daemon=True)
    thread.start()

    os.system(
        f'docker run -p 8888:8888 --runtime=nvidia -v{mapping_directory}:/notebooks  --name {docker_name} -it tensorflow-gpu-vim'
    )

if __name__ == '__main__':
    start_tensorflow_docker()
