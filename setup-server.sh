#!/bin/bash

cd ~/hchq
sudo pkill memcached
sudo pkill mysqld
sudo pkill nginx
sudo pkill python

sudo /etc/init.d/memcached restart
sudo /etc/init.d/mysql restart
sudo /etc/init.d/nginx restart
python server.py
