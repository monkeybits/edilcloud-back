#!/bin/bash

chmod -R 777 /var/spool/cron || exit 1
exec "$@"
#"chmod -R 777 /var/spool/cron", "redis-server", "--appendonly", "yes"]