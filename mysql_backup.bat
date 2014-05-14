@echo off
set today=%date:~0,4%%date:~5,2%%date:~8,2%
set sql=hchq_%today%.sql
set backup_path=E:\work\mysql_backup
set mysql_bin=C:\Program Files\MySQL\MySQL Server 5.6\bin
C:
cd %mysql_bin%
echo backup %sql%...
mysqldump.exe --opt -uroot -p2011 hchq > %backup_path%\%sql%
echo %sql% backup success!

echo backup photos...

xcopy e:\work\hchq\static\images\photos e:\work\mysql_backup\photos /s /e /y
xcopy e:\work\hchq\static\images\thumbnails e:\work\mysql_backup\thumbnails /s /e /y

echo photos backup success!

