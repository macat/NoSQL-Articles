import json
from time import time
import tornado.httpserver
import tornado.ioloop
import tornado.web
import redis

class TimelineHandler(tornado.web.RequestHandler):
    def post(self, event):
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.lpush(event, '%d|%s|%s' % (int(time()), self.get_argument('user'), self.get_argument('message')))
        self.write('ok')

    def get(self, event):
        r = redis.Redis(host='localhost', port=6379, db=0)
        out = []
        for post in r.lrange(event, 0, 30):
            time, user, message = post.split('|')
            out.append({'time': time, 'user': user, 'message': message})

        self.set_header('Content-type', 'json/application')
        self.write(json.dumps(out))

application = tornado.web.Application([
    (r'/timeline/(\w+)', TimelineHandler),
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

