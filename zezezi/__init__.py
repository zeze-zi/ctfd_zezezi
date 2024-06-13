# import fcntl
import warnings

import requests
from flask import Blueprint, render_template, session, current_app, request
from flask_apscheduler import APScheduler

from CTFd.api import CTFd_API_v1
from CTFd.plugins import (
    register_plugin_assets_directory,
    register_admin_plugin_menu_bar,
)
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.utils import get_config, set_config
from CTFd.utils.decorators import admins_only

from .api import user_namespace, admin_namespace, AdminContainers
from .challenge_type import DynamicValueDockerChallenge

from .utils.routers import Router


class WhaleChecks:
    pass


def load(app):
    # upgrade()
    plugin_name = __name__.split('.')[-1]
    set_config('zezezi:plugin_name', plugin_name)
    set_config('zezezi:host', "192.168.40.133")
    app.db.create_all()

    register_plugin_assets_directory(
        app, base_path=f"/plugins/{plugin_name}/assets",
        endpoint='plugins.zezezi.assets'
    )
    register_admin_plugin_menu_bar(
        title='zezezi',
        route='/plugins/zezezi/admin/containers'
    )

    DynamicValueDockerChallenge.templates = {
        "create": f"/plugins/{plugin_name}/assets/create.html",
        "update": f"/plugins/{plugin_name}/assets/update.html",
        "view": f"/plugins/{plugin_name}/assets/view.html",
    }
    DynamicValueDockerChallenge.scripts = {
        "create": "/plugins/zezezi/assets/create.js",
        "update": "/plugins/zezezi/assets/update.js",
        "view": "/plugins/zezezi/assets/view.js",
    }
    CHALLENGE_CLASSES["zezezi_dynamic_docker"] = DynamicValueDockerChallenge

    page_blueprint = Blueprint(
        "zezezi",
        __name__,
        template_folder="templates",
        static_folder="assets",
        url_prefix="/plugins/zezezi"
    )

    @page_blueprint.route("/admin/containers")
    @admins_only
    def admin_list_containers():
        result = AdminContainers.get()
        return render_template("zezezi_containers.html",
                               plugin_name=plugin_name,
                               containers=result['data']['containers'],
                               pages=result['data']['pages'],
                               curr_page=abs(request.args.get("page", 1, type=int)),
                               curr_page_start=result['data']['page_start'])

    CTFd_API_v1.add_namespace(admin_namespace, path="/plugins/zezezi/admin")
    CTFd_API_v1.add_namespace(user_namespace, path="/plugins/zezezi")

    app.register_blueprint(page_blueprint)
