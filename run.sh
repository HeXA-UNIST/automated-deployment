#!/bin/bash
gunicorn main:app --access-logfile `pwd`/access.log --error-logfile `pwd`/error.log -b 0.0.0.0:5555 -w 4 --timeout=10 -k gevent --daemon
