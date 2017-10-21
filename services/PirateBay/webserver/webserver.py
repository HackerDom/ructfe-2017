from hashlib import sha512
from random import choice
from string import hexdigits
from base64 import b64encode, b64decode


import cherrypy
from jinja2 import Template

from db.client import DBClient
from db.model import Model, TextField, IntField
from torrent_format.torrent_file import TorrentFileInfo

TEMPLATES = [
    'main',
    'signup',
    'signin',
    'files_storage',
]


def get_sha512(data: bytes):
    hasher = sha512()
    hasher.update(data)
    return hasher.digest()


class UserError(Exception):
    def __init__(self, error_message):
        self.error_message = error_message


class User(Model):
    login = TextField(256)
    password = TextField(256)
    uid = TextField(32)


class Cookie:
    def __init__(self, uid, max_age, login, password):
        self.uid = uid
        self.max_age = max_age
        self.secret = Cookie.generate_cookie_secret(uid, login, password)

    @staticmethod
    def generate_cookie_secret(uid, login, password):
        res = b64encode(get_sha512((login + password + uid).encode())).decode()
        return res

    @staticmethod
    def validate(cookie_uid, cookie_secret):
        users = User.filter(uid=cookie_uid)
        if not users:
            raise UserError("invalid cookie")
        user = users[0]
        if Cookie.generate_cookie_secret(user.uid, user.login, user.password) != cookie_secret:
            raise UserError("invalid cookie")


def load_templates():
    templates_dict = {}
    for template_name in TEMPLATES:
        with open('templates/{}.html'.format(template_name)) as template_file:
            templates_dict[template_name] = Template(template_file.read())
    return templates_dict


def generate_uid():
    return ''.join(choice(hexdigits) for _ in range(32))


def register(login, password):
    users = User.filter(login=login)
    if users:
        raise UserError("user {} already exists".format(login))
    User.create(uid=generate_uid(), login=login, password=password)


def authenticate(login, password):
    users = User.filter(login=login)
    if not users:
        raise UserError("user {} doesn't exists".format(login))
    user = users[0]
    if user.password != password:
        raise UserError("wrong password")
    return user.uid


def get_torrent_info_files():
    files = TorrentFileInfo.all()
    return files


class RequestHandler:
    def __init__(self):
        self.templates_dict = load_templates()

    def get_template(self, template_name):
        return self.templates_dict[template_name]

    @cherrypy.expose
    def signin(self, login, password):
        try:
            user_id = authenticate(login, password)
            user_cookie = Cookie(user_id, 10, login, password)

            cookie = cherrypy.response.cookie

            cookie['uid'] = user_cookie.uid
            cookie['uid']['max-age'] = 10

            cookie['secret'] = user_cookie.secret
            cookie['secret']['max-age'] = 10

            return self.get_template('main').render(message='user "{}" has been successfully signed in'.format(login))
        except UserError as user_error:
            return self.get_template('signin').render(message=user_error.error_message)

    @cherrypy.expose
    def signup(self, login, password):
        try:
            register(login, password)
            return self.get_template('main').render(message='user "{}" has been successfully signed up'.format(login))
        except UserError as user_error:
            return self.get_template('signup').render(message=user_error.error_message)

    @cherrypy.expose
    def signup_page(self):
        return self.get_template('signup').render()

    @cherrypy.expose
    def signin_page(self):
        return self.get_template('signin').render()

    @cherrypy.expose
    def index(self):
        requset_cookie = dict(cherrypy.request.cookie)
        if 'uid' in requset_cookie:
            secret = requset_cookie['secret'].value
            uid = requset_cookie['uid'].value
            Cookie.validate(uid, secret)

        return self.get_template('main').render()

    @cherrypy.expose
    def storage(self):
        return self.get_template('files_storage').render(
            model_fields=TorrentFileInfo.get_field_names(),
            files=get_torrent_info_files(),
        )


def start_web_server():
    with DBClient() as db_client:
        db_client.connection.commit()
        request_handler = RequestHandler()
        cherrypy.quickstart(request_handler, '/', config='webserver.config')


if __name__ == '__main__':
    start_web_server()
