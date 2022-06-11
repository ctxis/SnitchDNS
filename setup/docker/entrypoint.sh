#!/bin/bash

service apache2 start
service cron start

./venv.sh flask snitch_start
./venv.sh flask run --host 127.0.0.1 --port 8888
