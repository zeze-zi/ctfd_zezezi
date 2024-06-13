from datetime import datetime

from flask import request


from CTFd.utils import get_config
from CTFd.utils import user as current_user
from CTFd.utils.decorators import admins_only, authed_only
from .utils.control import ControlUtil
from .utils.db import DBContainer
from flask_restx import Namespace, Resource, abort
admin_namespace = Namespace("zezezi-admin")
user_namespace = Namespace("zezezi-user")


@admin_namespace.errorhandler
@user_namespace.errorhandler
def handle_default(err):
    return {
        'success': False,
        "message": 'Unexpected things happened'
    }, 500


@admin_namespace.route('/container')
class AdminContainers(Resource):
    @staticmethod
    @admins_only
    def get():
        page = abs(request.args.get("page", 1, type=int))
        results_per_page = abs(request.args.get("per_page", 20, type=int))
        page_start = results_per_page * (page - 1)
        page_end = results_per_page * (page - 1) + results_per_page

        count = DBContainer.get_all_alive_container_count()
        containers = DBContainer.get_all_alive_container_page(
            page_start, page_end)

        return {'success': True, 'data': {
            'containers': containers,
            'total': count,
            'pages': int(count / results_per_page) + (count % results_per_page > 0),
            'page_start': page_start,
        }}

    @staticmethod
    @admins_only
    def patch():
        user_id = request.args.get('user_id', -1)
        challenge_id = request.args.get('challenge_id', -1)
        result, message = ControlUtil.try_renew_container(user_id=int(user_id), challenge_id=int(challenge_id))
        if not result:
            abort(403, message, success=False)
        return {'success': True, 'message': message}

    @staticmethod
    @admins_only
    def delete():
        user_id = request.args.get('user_id')
        challenge_id = request.args.get('challenge_id')
        result, message = ControlUtil.try_remove_container(user_id, challenge_id)
        return {'success': result, 'message': message}


@user_namespace.route("/container")
class UserContainers(Resource):
    @staticmethod
    @authed_only
    def get():
        print("访问测试点1")
        user_id = current_user.get_current_user().id
        challenge_id = request.args.get('challenge_id')
        print(user_id, challenge_id)
        container = DBContainer.get_current_containers(user_id=user_id, challenge_id=challenge_id)
        if not container:
            return {'success': True, 'data': {}}
            # return {"success": True, "data": {"lan_domain": "1-e202c852-e645-4a3d-bcf0-6595de8c2d57", "user_access": "<a target=\"_blank\" href=\"http://10.20.3.10:50198\">http://10.20.3.10:50198</a>", "remaining_time": 3600}}
        timeout = int(get_config("zezezi:docker_timeout", "3600"))
        if int(container.challenge_id) != int(challenge_id):
            return abort(403, f'Container started but not from this challenge ({container.challenge.name})', success=False)
        print(type(container.start_time))
        print("访问测试点1port",container.port)
        return {
            'success': True,
            'data': {
                'lan_domain': str(user_id) + "-" + container.uuid,
                'user_access': "<a target=\"_blank\" href=\"http://"+get_config('zezezi:host')+":"+str(container.port)+"\">http://"+get_config("zezezi:host")+":"+str(container.port)+"</a>",
                'remaining_time': timeout - (datetime.now() - container.start_time).seconds,
            }
        }

    @staticmethod
    @authed_only
    def post():
        user_id = current_user.get_current_user().id
        # ControlUtil.try_remove_container(user_id)

        challenge_id = request.args.get('challenge_id')
        print("访问post测试点2")
        print(user_id,challenge_id)
        result, message = ControlUtil.try_add_container(
            user_id=user_id,
            challenge_id=challenge_id
        )
        if not result:
            abort(403, message, success=False)
        return {'success': result, 'message': message}

    @staticmethod
    @authed_only
    def patch():
        user_id = current_user.get_current_user().id
        challenge_id = request.args.get('challenge_id')
        docker_max_renew_count = int(get_config("zezezi:docker_max_renew_count", 5))
        container = DBContainer.get_current_containers(user_id, challenge_id)
        if container is None:
            abort(403, 'Instance not found.', success=False)
        if int(container.challenge_id) != int(challenge_id):
            abort(403, f'Container started but not from this challenge（{container.challenge.name}）', success=False)
        if container.renew_count >= docker_max_renew_count:
            abort(403, 'Max renewal count exceed.', success=False)
        result, message = ControlUtil.try_renew_container(user_id=user_id, challenge_id=challenge_id)
        return {'success': result, 'message': message}

    @staticmethod
    @authed_only
    def delete():
        user_id = current_user.get_current_user().id
        challenge_id = request.args.get('challenge_id')
        result, message = ControlUtil.try_remove_container(user_id, challenge_id)
        if not result:
            abort(403, message, success=False)
        return {'success': True, 'message': message}
