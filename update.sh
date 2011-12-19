cd e:/work/hchq
pwd
status=$(git fetch)
echo $status
if [ -z $status];then
    echo u'the source code is clean and don`t update!!!'
else
    echo u'the source code need to update!!!'
    git merge origin/develop
    echo 'the source code has updated!!!'
    git status
    echo u'restart apache demo!!!'
    net stop Apache2.2
    net start Apache2.2
fi

