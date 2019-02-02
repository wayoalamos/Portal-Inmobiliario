"""
This module will listen to queued tasks and process them as they are received.
"""


import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()

"""
for heroku:
    redis_url = os.getenv('REDISTOGO_URL')
    urlparse.uses_netloc.append('redis')
    url = urlparse.urlparse(redis_url)
    conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)
"""
