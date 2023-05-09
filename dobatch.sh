#!/bin/bash
LOCK_FILE="/tmp/batch_$1.lock"
if [ -f $LOCK_FILE ]; then
  echo "batch_$1.py is already running" >> ../log/batch_$1.log 2>&1
  exit 1
else
  touch $LOCK_FILE
fi
docker exec back$2 python3 batch_$1.py >> ../log/batch_$1.log 2>&1
rm $LOCK_FILE
