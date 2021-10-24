#!/usr/bin/env bash

SSH_USER=nlmaps
SSH_HOST=nlmaps

THIS_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DEPLOY_SCRIPT="$THIS_DIR/deploy.sh"

scp "$DEPLOY_SCRIPT" "$SSH_USER@$SSH_HOST:/tmp/deploy.sh"

NLMAPS_WEB_PROD_INI="$THIS_DIR/../nlmaps-web-prod.ini"
if [ -f "$NLMAPS_WEB_PROD_INI" ]; then
    scp "$NLMAPS_WEB_PROD_INI" "$SSH_USER@$SSH_HOST:/tmp/nlmaps-web.ini"
    ssh "$SSH_USER@$SSH_HOST" bash /tmp/deploy.sh -i '/tmp/nlmaps-web.ini' "$@"
else
    echo 'Warning: No secret ini file nlmaps-web-prod.ini present in repo.'
    ssh "$SSH_USER@$SSH_HOST" bash /tmp/deploy.sh "$@"
fi

