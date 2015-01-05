#!/bin/bash
cd
rm -rf hchq_bk
mv hchq hchq_bk
git clone https://github.com/bright-pan/hchq
cp -rf hchq_bk/static/images/photos hchq/static/images/
cp -rf hchq_bk/static/images/thumbnails hchq/static/images/
cd hchq/mysql_backup
./mysql_backup.sh
cd ~/hchq
mv mysql_backup ../
./dist.sh
