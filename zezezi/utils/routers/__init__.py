from datetime import datetime
from CTFd.utils import get_config


def instanciate(cls):
    return cls()

@instanciate
class Router:
    _name = ''
    _router = None

    @classmethod
    def register(cls, container):
        print(container.port)
        user_id=container.user_id
        print("user_id:",user_id)
        timeout = int(get_config("zezezi:docker_timeout", "3600"))
        return True, {'data': {
                'lan_domain': str(user_id) + "-" + container.uuid,
                'user_access': "<a target=\"_blank\" href=\""+get_config("zezezi:host")+":"+str(container.port)+"\">http://"+get_config("zezezi:host")+":"+str(container.port)+"</a>",
                'remaining_time': timeout - (datetime.now() - container.start_time).seconds,
            }}

    @classmethod
    def unregister(cls, container):
        print("unregistercs1:",container.uuid)
        return True, {'data': {}}

    @staticmethod
    def reset():
        Router._name = ''
        Router._router = None

__all__ = ["Router"]
