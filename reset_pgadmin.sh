#!/bin/bash

# Kill all possible previous pgadmin processes:
for pid in $(pgrep -i pgadmin)
do
  kill -9 $pid
done

# Open new pgadmin process:
open -a pgAdmin\ 4