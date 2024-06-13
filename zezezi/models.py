import random
import uuid
from datetime import datetime

from jinja2 import Template

from CTFd.utils import get_config
from CTFd.models import db, Challenges


class DynamicDockerChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "zezezi_dynamic_docker"}
    id = db.Column(None, db.ForeignKey("challenges.id",
                                       ondelete="CASCADE"), primary_key=True)

    initial = db.Column(db.Integer, default=0)
    minimum = db.Column(db.Integer, default=0)
    decay = db.Column(db.Integer, default=0)
    memory_limit = db.Column(db.Text, default="128m")
    cpu_limit = db.Column(db.Float, default=0.5)
    dynamic_score = db.Column(db.Integer, default=0)

    docker_image = db.Column(db.Text, default=0)
    redirect_type = db.Column(db.Text, default=0)
    docker_port = db.Column(db.Integer, default=80)
    function = db.Column(db.String(32), default="logarithmic")

    def __init__(self, *args, **kwargs):
        super(DynamicDockerChallenge, self).__init__(**kwargs)
        self.initial = kwargs["value"]


class ZezeziContainer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(None, db.ForeignKey("users.id"))
    challenge_id = db.Column(None, db.ForeignKey("challenges.id"))
    start_time = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    renew_count = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.Integer, default=1)
    uuid = db.Column(db.String(256))
    port = db.Column(db.Integer, nullable=True, default=0, unique=True)
    flag = db.Column(db.String(128), nullable=False)
    docker_port = db.Column(db.Integer, default=80)

    # Relationships
    user = db.relationship(
        "Users", foreign_keys="ZezeziContainer.user_id", lazy="select")
    challenge = db.relationship(
        "DynamicDockerChallenge", foreign_keys="ZezeziContainer.challenge_id", lazy="select"
    )

    def get_port(self, start=20000, end=21000):
        while True:
            random_number = random.randint(start, end)
            if ZezeziContainer.query.filter_by(port=random_number).first():
                continue
            else:
                return random_number

    def __init__(self, user_id, challenge_id):
        self.user_id = user_id
        self.challenge_id = challenge_id
        self.start_time = datetime.now()
        self.renew_count = 0
        self.uuid = str(uuid.uuid4())
        self.flag = Template(get_config(
            'zezezi:template_chall_flag', '{{ "flag{"+uuid.uuid4()|string+"}" }}'
        )).render(container=self, uuid=uuid, random=random, get_config=get_config)
        self.port = self.get_port()
        self.docker_port = DynamicDockerChallenge.query.filter(DynamicDockerChallenge.id==challenge_id).first().docker_port


    def __repr__(self):
        return "<ZezeziContainer ID:{0} {1} {2} {3} {4}>".format(self.id, self.user_id, self.challenge_id,
                                                                 self.start_time, self.renew_count)
