import os
import sys

sys.path.insert(0, os.path.expanduser('~/app'))
from flup.server.fcgi import WSGIServer
from app import app

if __name__ == '__main__':
    WSGIServer(app).run()