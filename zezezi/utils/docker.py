import json
import random
import uuid
from collections import OrderedDict

import docker
from flask import current_app

from CTFd.utils import get_config


# from .cache import CacheProvider
from .exceptions import ZezeziError
from ..models import DynamicDockerChallenge

###连接docker
def get_docker_client():
    try:
        print("开始连接docker")
        client = docker.from_env()
        print("连接成功")
        return client
    except docker.errors.DockerException as e:
        print(f"连接 Docker 出现错误: {e}")
        return None

class DockerUtils:
    client = get_docker_client()


    ###初始化
    @staticmethod
    def init():
        print("初始化DockerUtils")
        try:
            print("正常进入")
            DockerUtils.client = get_docker_client()
        except Exception:
            raise ZezeziError(
                'Docker Connection Error\n'
                'Please ensure the docker api url (first config item) is correct\n'
                'if you are using unix:///var/run/docker.sock, check if the socket is correctly mapped'
            )
        credentials = get_config("zezezi:docker_credentials")
        if credentials and credentials.count(':') == 1:
            try:
                DockerUtils.client.login(*credentials.split(':'))
            except Exception:
                raise ZezeziError('docker.io failed to login, check your credentials')

    ####添加容器
    @staticmethod
    def add_container(container):
        DockerUtils._create_standalone_container(DockerUtils.client, container)
    ####运行容器
    @staticmethod
    def _create_standalone_container(client, container):
        print("container.challenge.docker_image",container.challenge.docker_image)
        image=str(str(container.challenge.docker_image).split(":")[0])
        docker_port=str(container.docker_port)+'/tcp'
        client.containers.run(
            image=image,
            name=container.uuid,
            environment={'FLAG': container.flag},
            detach=True,
            ports={docker_port: container.port},
        )
        return container.port
    ###删除
    @staticmethod
    def remove_container(container):
        name=container.uuid
        for i in DockerUtils.client.containers.list(all=True):
            if i.name == name:
                DockerUtils.client.containers.get(i.id).remove(force=True)
                print("删除测试功能点1：", i.id)
    ###延长时间
    @staticmethod
    def convert_readable_text(text):
        lower_text = text.lower()
        if lower_text.endswith("k"):
            return int(text[:-1]) * 1024
        if lower_text.endswith("m"):
            return int(text[:-1]) * 1024 * 1024

        if lower_text.endswith("g"):
            return int(text[:-1]) * 1024 * 1024 * 1024
        return 0


