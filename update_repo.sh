
#!/bin/bash
CWD=$1
REPO_SRC=$2
REPO_ORIGIN=$3
cd $CWD
if [ ! -d $REPO_SRC ]
then
    git clone $REPO_ORIGIN $REPO_SRC
else
    pushd $REPO_SRC
    git pull
    popd
fi