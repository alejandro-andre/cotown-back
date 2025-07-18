#!/bin/bash
LOCK_FILE="/tmp/batch_$1.lock"
if [ -f $LOCK_FILE ]; then
  echo "batch_$1.py is already running"
  exit 1
else
  touch $LOCK_FILE
fi
docker exec back python3 batch_$1.py
rm $LOCK_FILE
