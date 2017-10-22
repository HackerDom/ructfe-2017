import os
from hashlib import sha512
from base64 import b64encode

import cherrypy
from jinja2 import Template

from db.client import DBClient
from db.model import Model, TextField
from torrent_format.torrent_file import TorrentFileInfo
from utils import generate_uid

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

    @staticmethod
    def get_user_by_id(uid):
        users = User.filter(uid=uid)
        if not users:
            return None
        return users[0]


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
    def is_valid(cookie_uid, cookie_secret):
        user = User.get_user_by_id(cookie_uid)
        if user is None:
            return False
        if Cookie.generate_cookie_secret(user.uid, user.login, user.password) != cookie_secret:
            return False
        return True


def load_templates():
    templates_dict = {}
    for template_name in TEMPLATES:
        with open('webserver/templates/{}.html'.format(template_name)) as template_file:
            templates_dict[template_name] = Template(template_file.read())
    return templates_dict


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


def get_authorized_user():
    request_cookie = dict(cherrypy.request.cookie)
    if ('uid' in request_cookie) and ('secret' in request_cookie):
        secret = request_cookie['secret'].value
        uid = request_cookie['uid'].value
        if Cookie.is_valid(uid, secret):
            return User.get_user_by_id(uid)
    return None


def set_cookie(login, password):
    user_id = authenticate(login, password)
    user_cookie = Cookie(user_id, 60 * 5, login, password)
    response_cookie = cherrypy.response.cookie
    response_cookie['uid'] = user_cookie.uid
    response_cookie['uid']['max-age'] = user_cookie.max_age
    response_cookie['secret'] = user_cookie.secret
    response_cookie['secret']['max-age'] = user_cookie.max_age


def reset_cookie():
    response_cookie = cherrypy.response.cookie
    response_cookie['uid'] = ''
    response_cookie['uid']['max-age'] = 0
    response_cookie['secret'] = ''
    response_cookie['secret']['max-age'] = 0


class RequestHandler:
    def __init__(self):
        self.templates_dict = load_templates()

    def get_template(self, template_name):
        return self.templates_dict[template_name]

    @cherrypy.expose
    def signin(self, login, password):
        try:
            set_cookie(login, password)
            raise cherrypy.HTTPRedirect('/')
        except UserError as user_error:
            return self.get_template('signin').render(message=user_error.error_message)

    @cherrypy.expose
    def signup(self, login, password):
        try:
            register(login, password)
            set_cookie(login, password)
            raise cherrypy.HTTPRedirect('/')
        except UserError as user_error:
            return self.get_template('signup').render(message=user_error.error_message)

    @cherrypy.expose
    def signup_page(self):
        return self.get_template('signup').render()

    @cherrypy.expose
    def signin_page(self):
        return self.get_template('signin').render()

    @cherrypy.expose
    def signout(self):
        reset_cookie()
        raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def index(self):
        user = get_authorized_user()
        if user is not None:
            signedin = True
            message = "Hello, {}!".format(user.login)
        else:
            signedin = False
            message = "Sign in for upload file!"
        return self.get_template('main').render(signedin=signedin, message=message)

    @cherrypy.expose
    def storage(self):
        if get_authorized_user() is None:
            raise cherrypy.HTTPRedirect('/')
        return self.get_template('files_storage').render(
            model_fields=TorrentFileInfo.get_field_names(),
            files=get_torrent_info_files(),
        )

    @cherrypy.expose
    def upload(self, upload_file):
        raw_torrent_info_file = bytearray()
        while True:
            data = upload_file.file.read(8192)
            if not data:
                break
            raw_torrent_info_file += data
        user_login = get_authorized_user().login
        TorrentFileInfo(bytes(raw_torrent_info_file), upload_by=user_login).save()
        raise cherrypy.HTTPRedirect('/storage')


def start_web_server():
    with DBClient() as db_client:
        db_client.connection.commit()
        request_handler = RequestHandler()
        cherrypy.quickstart(request_handler, '/', config='webserver/webserver.config')
