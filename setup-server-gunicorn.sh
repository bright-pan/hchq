#!/bin/bash

cd ~/hchq
sudo pkill memcached
sudo pkill mysqld
sudo pkill nginx
sudo pkill gunicorn

sudo /etc/init.d/memcached restart
sudo /etc/init.d/mysql restart
sudo /etc/init.d/nginx restart
gunicorn -k gevent -w 4 hchq.wsgi:application -b 127.0.0.1:8000
