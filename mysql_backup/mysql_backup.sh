#!/bin/bash
filename=`date +%Y%m%d`

mysqldump -uroot -phchq2010-2014*.* hchq | gzip > hchq-$filename.sql.gz

cd ../static/images/
tar czf ../../mysql_backup/photos.tar.gz photos
tar czf ../../mysql_backup/thumbnails.tar.gz thumbnails

