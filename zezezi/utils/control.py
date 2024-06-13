import datetime
import traceback

from CTFd.utils import get_config
from .db import DBContainer, db
from .docker import DockerUtils
from .routers import Router


class ControlUtil:
    @staticmethod
    def try_add_container(user_id, challenge_id):
        container = DBContainer.get_current_containers(user_id=user_id, challenge_id=challenge_id)
        if not container:   # 不要再次重新创建相同质询的容器（防止滥用）
            container = DBContainer.create_container_record(user_id, challenge_id)
            try:
                print("container:", container)
                port=DockerUtils.add_container(container)
            except Exception as e:
                DBContainer.remove_container_record(user_id, challenge_id)
                print(traceback.format_exc())
                return False, 'Docker 创建错误'
            print("container:", container.port)
            ok, msg = Router.register(container)
            if not ok:
                DockerUtils.remove_container(container)
                DBContainer.remove_container_record(user_id, challenge_id)
                return False, msg
            return True, 'Container created'
        else:
            return False, 'Container already exists'

    @staticmethod
    def try_remove_container(user_id, challenge_id):
        print("进入删除")
        container = DBContainer.get_current_containers(user_id=user_id, challenge_id=challenge_id)
        if not container:
            return False, '没有这样的容器'
        for _ in range(3):  # 配置？饰演“onerror_retry_cnt”
            try:
                ok, msg = Router.unregister(container)
                if not ok:
                    return False, msg
                DockerUtils.remove_container(container)
                DBContainer.remove_container_record(user_id, challenge_id)
                return True, 'Container destroyed'
            except Exception as e:
                print(traceback.format_exc())
        return False, '销毁实例时失败，请联系管理员！'

    @staticmethod
    def try_renew_container(user_id, challenge_id):
        container = DBContainer.get_current_containers(user_id, challenge_id)
        if not container:
            return False, 'No such container'
        timeout = int(get_config("zezezi:docker_timeout", "3600"))
        container.start_time = container.start_time + \
                               datetime.timedelta(seconds=timeout)
        if container.start_time > datetime.datetime.now():
            container.start_time = datetime.datetime.now()
            # race condition? useless maybe?
            # useful when docker_timeout < poll timeout (10 seconds)
            # doesn't make any sense
        else:
            return False, 'Invalid container'
        container.renew_count += 1
        db.session.commit()
        return True, 'Container Renewed'
