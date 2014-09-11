filename=`date +%Y%m%d`

mysqldump -uroot -p2011 hchq | gzip > hchq-$filename.sql.gz

cd ../static/images/
tar czf ../../mysql_backup/photos.tar.gz photos 
tar czf ../../mysql_backup/thumbnails.tar.gz thumbnails

