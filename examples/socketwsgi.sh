#!/bin/bash

uwsgi --http :5000 --gevent 1000 --http-websockets --master --wsgi-file websock.py --callable app --socket /tmp/web.sock
