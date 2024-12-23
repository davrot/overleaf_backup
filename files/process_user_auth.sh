#!/bin/bash
# This script handles password authentication

if [ "$PAM_TYPE" != "auth" ]; then
    exit 1
fi

# Read password from stdin
PAM_PASSWORD=$(cat)
/usr/bin/python3 /auth_against_docker.py ${PAM_USER} ${PAM_PASSWORD}
AUTH_STATUS=$?

if [ $AUTH_STATUS -eq 0 ]; then
    exit 0
else
    exit 1
fi



