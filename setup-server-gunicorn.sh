#!/bin/bash

cd ~/hchq
sudo pkill memcached
sudo pkill mysqld
sudo pkill nginx
sudo pkill gunicorn

sudo /etc/init.d/memcached restart
sudo /etc/init.d/mysql restart
sudo /etc/init.d/nginx restart

gunicorn_django -k gevent -t 500 -w 2
