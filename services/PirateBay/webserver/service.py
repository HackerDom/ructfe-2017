import cherrypy

from db.client import DBClient


class RequestHandler:
    @cherrypy.expose
    def index(self):
        return \
            """ <html>
                <head>
                    <link rel="stylesheet" type="text/css" href="css/simple.css">
                </head>
                <body>
                    <div>
                        <p id="error">C<span>S</span>S</p>
                        <p id="code">w<span>o</span><span>rks!</span></p>
                    </div>
                </body>
                </html>"""


if __name__ == '__main__':
    with DBClient() as db_client:
        request_handler = RequestHandler()
        cherrypy.quickstart(request_handler, '/', config='webserver.config')
