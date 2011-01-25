import json
from time import time
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.database

"""
CREATE TABLE `timeline` (
  `event` varchar(32) NOT NULL,
  `time` int(10) unsigned NOT NULL,
  `user` varchar(32) NOT NULL,
  `message` varchar(150) NOT NULL,
  KEY `event` (`event`,`time` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""

def connect_to_db():
    return tornado.database.Connection('localhost', 'test', 'root', '')

class TimelineHandler(tornado.web.RequestHandler):
    def post(self, event):
        db = connect_to_db()
        db.execute('INSERT INTO timeline (event, time, user, message) VALUES ("%s", %s, "%s", "%s")',
                   event, int(time()), self.get_argument('user'), self.get_argument('message'))
        self.write('ok')

    def get(self, event):
        db = connect_to_db()
        out = []
        for post in db.query('SELECT * FROM timeline WHERE event = "%s" ORDER BY time DESC LIMIT 0,30', event):
            out.append({'time': post.time, 'user': post.user, 'message': post.message})

        self.set_header('Content-type', 'json/application')
        self.write(json.dumps(out))

application = tornado.web.Application([
    (r'/timeline/(\w+)', TimelineHandler),
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
