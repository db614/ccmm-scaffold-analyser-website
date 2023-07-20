#!/bin/sh
. venv/bin/activate
flask db upgrade
exec gunicorn -w 1 -b :5000 --access-logfile - --error-logfile - ccmmdb.__init__:app
