#!/bin/bash

python -O -m compileall ../hchq
find -name "*.py" -exec rm -f {} \;
rm -rf INSTALL mysql_backup mysql_backup.bat deploy.txt README update*.sh
