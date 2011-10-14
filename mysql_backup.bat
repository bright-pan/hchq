@echo off
:: 设置今天的日期
set today=%date:~0,4%%date:~5,2%%date:~8,2%
:: 用来备份的文件名
set sql=hchq_%today%.sql
:: 备份文件存储位置
set backup_path=E:\work\mysql_backup
:: mysql bin目录
set mysql_bin=C:\Program Files\MySQL\MySQL Server 5.1\bin

:: 开始数据备份，请修改-uroot中的root（数据库用户名）和-pezool_org中的ezool_org(数据库密码)
C:
cd %mysql_bin%
echo backup %sql%...
mysqldump.exe --opt -uroot -p2011 hchq > %backup_path%\%sql%
echo %sql% backup success!

echo backup photos...

xcopy e:\work\hchq\static\images\photos e:\work\mysql_backup\photos /s /e /y
xcopy e:\work\hchq\static\images\thumbnails e:\work\mysql_backup\thumbnails /s /e /y

echo photos backup success!

