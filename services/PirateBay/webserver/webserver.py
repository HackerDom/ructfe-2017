import os
import re

import cherrypy
from jinja2 import Template

from db.client import DBClient
from db.model import Model, TextField
from torrent_format.torrent_file import TorrentFile, PrivateTorrentFile
from utils import generate_uid, get_base_of_hash

LOGIN_PATTERN = re.compile("^[a-z0-9_-]{3,16}$")


class UserError(Exception):
    def __init__(self, error_message):
        self.error_message = error_message


class User(Model):
    login = TextField(256)
    password_hash = TextField(256)
    uid = TextField(32)

    @staticmethod
    def get_user_by_id(uid):
        users = User.filter(uid=uid)
        if not users:
            return None
        return users[0]


class Cookie:
    def __init__(self, uid, login, password, max_age=60 * 60):
        self.uid = uid
        self.max_age = max_age
        self.secret = Cookie.generate_cookie_secret(uid, login, get_base_of_hash(password))

    @staticmethod
    def generate_cookie_secret(uid, login, password_hash):
        return get_base_of_hash(login + password_hash + uid)

    @staticmethod
    def is_valid(cookie_uid, cookie_secret):
        user = User.get_user_by_id(cookie_uid)
        if user is None:
            return False
        if Cookie.generate_cookie_secret(user.uid, user.login, user.password_hash) != cookie_secret:
            return False
        return True


def load_templates():
    templates_dict = {}
    for template_name in os.listdir('webserver/templates'):
        with open('webserver/templates/{}'.format(template_name)) as template_file:
            templates_dict[template_name] = Template(template_file.read())
    return templates_dict


def validate_login(login):
    if re.match(LOGIN_PATTERN, login) is None:
        raise UserError('Username "{}" is invalid. Username must match regex {}.'.format(login, LOGIN_PATTERN.pattern))


BAD_CHARS = [
    '\\',
    '\'',
    '\"',
    '%',
    '_',
]


def adjust_search_filter(filter_req: str):
    for bad_char in BAD_CHARS:
        filter_req = filter_req.replace(bad_char, "\\" + bad_char)
    return filter_req


def register(login, password):
    validate_login(login)
    users = User.filter(login=login)
    if users:
        raise UserError('Username "{}" is already exists.'.format(login))
    User.create(uid=generate_uid(), login=login, password_hash=get_base_of_hash(password))


def authenticate(login, password):
    users = User.filter(login=login)
    if not users:
        raise UserError("User {} doesn't exists.".format(login))
    user = users[0]
    if user.password_hash != get_base_of_hash(password):
        raise UserError("Wrong password.")
    return user.uid


LINES_FOR_QUERY = 20


def error_page_404(status, message, traceback, version):
    return "404 Error!"


def get_torrent_files(fields_filter, page_number):
    if fields_filter:
        files = TorrentFile.filter(name__contains=fields_filter)
    else:
        files = TorrentFile.all(page_number * LINES_FOR_QUERY, LINES_FOR_QUERY)
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
    user_cookie = Cookie(user_id, login, password)
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
        self.error = ""

    def get_template(self, template_name):
        return self.templates_dict[template_name]

    @cherrypy.expose
    def signin(self, login, password):
        try:
            set_cookie(login, password)
            self.error = ""
            raise cherrypy.HTTPRedirect('/')
        except UserError as user_error:
            self.error = str(user_error)
            raise cherrypy.HTTPRedirect('/signin_page')

    @cherrypy.expose
    def signup(self, login, password):
        try:
            register(login, password)
            set_cookie(login, password)
            self.error = ""
            raise cherrypy.HTTPRedirect('/')
        except UserError as user_error:
            self.error = user_error
            raise cherrypy.HTTPRedirect('/signup_page')

    @cherrypy.expose
    def signup_page(self):
        return self.get_template('signup.html').render(error_message=self.error)

    @cherrypy.expose
    def signin_page(self):
        return self.get_template('signin.html').render(error_message=self.error)

    @cherrypy.expose
    def signout(self):
        reset_cookie()
        raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def index(self):
        user = get_authorized_user()
        authed = "" if user is None else user.login
        return self.get_template('main.html').render(authed=authed)

    @cherrypy.expose
    def default(self, _):
        return self.get_template('page_404.html').render()

    @cherrypy.expose
    def storage(self, search_filter="", page_number=0):
        user = get_authorized_user()
        if user is None:
            raise cherrypy.HTTPRedirect("/index")
        else:
            authed = user.login
        if not search_filter:
            max_page = int(TorrentFile.get_count() / LINES_FOR_QUERY)
            if (int(page_number) < 0) or (int(page_number) > max_page):
                raise cherrypy.HTTPError(404)
        else:
            max_page = -1
            page_number = 0
        return self.get_template('files_storage.html').render(
            model_fields=TorrentFile.get_field_names(),
            files=get_torrent_files(adjust_search_filter(search_filter), int(page_number)),
            authed=authed,
            value=search_filter,
            page_number=page_number,
            max_page=max_page,
        )

    @cherrypy.expose
    def private_storage(self, search_filter="", page_number="0"):
        user = get_authorized_user()
        if user is None:
            raise cherrypy.HTTPRedirect('/index')
        if search_filter:
            max_page = -1
            files = PrivateTorrentFile.filter(
                name__contains=adjust_search_filter(search_filter),
                upload_by=user.login
            )
        else:
            max_page = int(len(PrivateTorrentFile.filter(upload_by=user.login)) / LINES_FOR_QUERY)
            files = PrivateTorrentFile.filter(
                lower_bound=int(page_number) * LINES_FOR_QUERY,
                count=LINES_FOR_QUERY,
                upload_by=user.login
            )
        return self.get_template('private_files_storage.html').render(
            model_fields=PrivateTorrentFile.get_field_names(),
            files=files,
            authed=user.login,
            value=search_filter,
            max_page=max_page,
            page_number=page_number,
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
        TorrentFile(bytes(raw_torrent_info_file), upload_by=user_login).save()
        raise cherrypy.HTTPRedirect('/storage')

    @cherrypy.expose
    def upload_file(self):
        user = get_authorized_user()
        if user is None:
            raise cherrypy.HTTPRedirect('/')
        return self.get_template('upload_file.html').render(authed=user.login)

    @cherrypy.expose
    def download(self, file_id):
        tfiles = TorrentFile.filter(uid=file_id)
        if (len(tfiles) > 1) or (not tfiles):
            raise cherrypy.HTTPError(404)
        tfile = tfiles[0]
        cherrypy.response.headers['Content-Type'] = 'application/x-bittorrent'
        cherrypy.response.headers['Content-Disposition'] = 'attachment; filename="{}.torrent"'.format(tfile.name)
        return tfile.get_data()

    @cherrypy.expose
    def download_private(self, file_id):
        user = get_authorized_user()
        if user is None:
            raise cherrypy.HTTPError(404)
        tfiles = PrivateTorrentFile.filter(uid=file_id)
        if (len(tfiles) > 1) or (not tfiles):
            raise cherrypy.HTTPError(404)
        tfile = tfiles[0]
        if user.login != tfile.upload_by:
            raise cherrypy.HTTPError(404)
        cherrypy.response.headers['Content-Type'] = 'application/x-bittorrent'
        cherrypy.response.headers['Content-Disposition'] = 'attachment; filename="{}.torrent"'.format(tfile.name)
        return tfile.get_data()

    @cherrypy.expose
    def upload_private(self, upload_file):
        raw_torrent_info_file = bytearray()
        while True:
            data = upload_file.file.read(8192)
            if not data:
                break
            raw_torrent_info_file += data
        user_login = get_authorized_user().login
        PrivateTorrentFile(bytes(raw_torrent_info_file), upload_by=user_login).save()

        raise cherrypy.HTTPRedirect('/storage')


def start_web_server():
    with DBClient() as db_client:
        db_client.connection.commit()
        request_handler = RequestHandler()
        cherrypy.quickstart(request_handler, '/', config='webserver/webserver.config')
