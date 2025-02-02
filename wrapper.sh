#!/bin/bash

# Start marktplaats-notif
python -m marktplaats-notif

# Start web UI
gunicorn -b 0.0.0.0:$PORT server:app &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
