#!/bin/bash

echo "****************************************"
echo "Archiving for hchq $1"
git archive --format=tar --prefix=hchq/ $1 | (cd .. && gzip > hchq-$1.tar.gz)
echo "Complete archive hchq $1"
echo "****************************************"
