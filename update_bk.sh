cd e:/work/hchq
pwd
git fetch
status=$(git status)
s=$(expr "$status" : ".*fast-forwarded.")
t="0"
echo $s
if [ "$s" = "$t" ];
then
    echo 'the source code is clean and do not update!!!'
else
    echo "the source code need to update!!!"
    git merge origin/develop
    echo "the source code has updated!!!"
    git status
    echo "restart apache demo!!!"
    net stop Apache2.2
    net start Apache2.2
fi
cmd /c mysql_backup.bat
