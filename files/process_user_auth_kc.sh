#!/bin/bash
# This script handles password authentication

if [ "$PAM_TYPE" != "auth" ]; then
    exit 1
fi

# Read password from stdin
PAM_PASSWORD=$(cat)
echo "$PAM_PASSWORD" | /etc/kc-ssh-pam/kc-ssh-pam -c /etc/kc-ssh-pam/config.toml
AUTH_STATUS=$?

if [ $AUTH_STATUS -eq 0 ]; then
    exit 0
else
    exit 1
fi



