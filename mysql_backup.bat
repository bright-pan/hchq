@echo off
:: ���ý��������
set today=%date:~0,4%%date:~5,2%%date:~8,2%
:: �������ݵ��ļ���
set sql=hchq_%today%.sql
:: �����ļ��洢λ��
set backup_path=E:\work\mysql_backup
:: mysql binĿ¼
set mysql_bin=C:\Program Files\MySQL\MySQL Server 5.1\bin

:: ��ʼ���ݱ��ݣ����޸�-uroot�е�root�����ݿ��û�������-pezool_org�е�ezool_org(���ݿ�����)
C:
cd %mysql_bin%
echo backup %sql%...
mysqldump.exe --opt -uroot -p2011 hchq > %backup_path%\%sql%
echo %sql% backup success!

echo backup photos...

xcopy e:\work\hchq\static\images\photos e:\work\mysql_backup\photos /s /e /y
xcopy e:\work\hchq\static\images\thumbnails e:\work\mysql_backup\thumbnails /s /e /y

echo photos backup success!

