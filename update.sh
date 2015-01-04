#!/bin/bash                                                                                                                                                           
cd
rm -rf hchq_bk hchq.zip
mv hchq hchq_bk
curl -L -o hchq.zip https://codeload.github.com/bright-pan/hchq/zip/master
unzip hchq.zip
mv hchq-master hchq
cp -rf hchq_bk/static/images/photos hchq/static/images/photos
cp -rf hchq_bk/static/images/thumbnails hchq/static/images/thumbnails
cd hchq/mysql_backup
./mysql_backup.sh

cd ~/hchq
mv mysql_backup ../
./dist.sh
