@echo off
set gevent_path=E:\work\hchq
set nginx_path=E:\work\hchq\nginx

cd %nginx_path%
echo enter %nginx_path%...
taskkill /f /t /im nginx.exe
start nginx.exe

cd %gevent_path%
echo enter %gevent_path%...
taskkill /f /t /im python.exe
start python server.py


