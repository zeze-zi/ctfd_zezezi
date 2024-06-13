import datetime

from CTFd.models import db
from CTFd.utils import get_config
from ..models import ZezeziContainer


class DBContainer:
    @staticmethod
    def create_container_record(user_id, challenge_id):
        container = ZezeziContainer(user_id=user_id, challenge_id=challenge_id)
        db.session.add(container)
        db.session.commit()
        print("create_container_record测试点")
        print(container)
        return container

    @staticmethod
    def get_current_containers(user_id, challenge_id):
        q = db.session.query(ZezeziContainer)
        q = q.filter(ZezeziContainer.user_id == user_id, ZezeziContainer.challenge_id == challenge_id)
        return q.first()

    @staticmethod
    def get_container_by_port(port):
        q = db.session.query(ZezeziContainer)
        q = q.filter(ZezeziContainer.port == port)
        return q.first()

    @staticmethod
    def remove_container_record(user_id, challenge_id):
        q = db.session.query(ZezeziContainer)
        q = q.filter(ZezeziContainer.user_id == user_id, ZezeziContainer.challenge_id == challenge_id)
        q.delete()
        db.session.commit()

    @staticmethod
    def get_all_expired_container():
        timeout = int(get_config("zezezi:docker_timeout", "3600"))

        q = db.session.query(ZezeziContainer)
        q = q.filter(
            ZezeziContainer.start_time <
            datetime.datetime.now() - datetime.timedelta(seconds=timeout)
        )
        return q.all()

    @staticmethod
    def get_all_alive_container():
        timeout = int(get_config("zezezi:docker_timeout", "3600"))

        q = db.session.query(ZezeziContainer)
        q = q.filter(
            ZezeziContainer.start_time >=
            datetime.datetime.now() - datetime.timedelta(seconds=timeout)
        )
        return q.all()

    @staticmethod
    def get_all_container():
        q = db.session.query(ZezeziContainer)
        return q.all()

    @staticmethod
    def get_all_alive_container_page(page_start, page_end):
        timeout = int(get_config("zezezi:docker_timeout", "3600"))

        q = db.session.query(ZezeziContainer)
        q = q.filter(
            ZezeziContainer.start_time >=
            datetime.datetime.now() - datetime.timedelta(seconds=timeout)
        )
        q = q.slice(page_start, page_end)
        return q.all()

    @staticmethod
    def get_all_alive_container_count():
        timeout = int(get_config("zezezi:docker_timeout", "3600"))

        q = db.session.query(ZezeziContainer)
        q = q.filter(
            ZezeziContainer.start_time >=
            datetime.datetime.now() - datetime.timedelta(seconds=timeout)
        )
        return q.count()



