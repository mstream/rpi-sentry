#! /usr/env bash

httping -c 1 -g http://localhost/status -s

if [[ $? -eq 0 ]]; then
    echo "Health check is OK."
else
    echo "Health check is not OK.. restarting service."
    sudo systemctl restart rpi-sentry.service
fi
