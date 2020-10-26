#!/bin/bash

chmod -R 777 /var/spool/cron || exit 1
exec "$@"