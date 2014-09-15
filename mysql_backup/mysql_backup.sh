#!/bin/bash
filename=`date +%Y%m%d`

mysqldump -uroot -phchq2010-2014*.* hchq | gzip > hchq-$filename.sql.gz

cd ../static/images/
tar czf ../../mysql_backup/photos.tar.gz photos
tar czf ../../mysql_backup/thumbnails.tar.gz thumbnails
cd ../../mysql_backup/
#gpg -a --output hchq-$filename.sql.gz.rsa -r bright_pan@163.com -e hchq-$filename.sql.gz
#gpg -a --output photos.tar.gz.rsa -r bright_pan@163.com -e photos.tar.gz
#gpg -a --output thumbnails.tar.gz.rsa -r bright_pan@163.com -e thumbnails.tar.gz
#rm -rf hchq-$filename.sql.gz photos.tar.gz thumbnails.tar.gz mysql_backup.sh
