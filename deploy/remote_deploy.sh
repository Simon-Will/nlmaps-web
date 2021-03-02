#!/usr/bin/env bash

SSH_USER=nlmaps
SSH_HOST=nlmaps

THIS_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DEPLOY_SCRIPT="$THIS_DIR/deploy.sh"

scp "$DEPLOY_SCRIPT" "$SSH_USER@$SSH_HOST:/tmp/deploy.sh"

NLMAPSWEB_PROD_INI="$THIS_DIR/../nlmapsweb-prod.ini"
if [ -f "$NLMAPSWEB_PROD_INI" ]; then
    scp "$NLMAPSWEB_PROD_INI" "$SSH_USER@$SSH_HOST:/tmp/nlmapsweb.ini"
    ssh "$SSH_USER@$SSH_HOST" bash /tmp/deploy.sh -i '/tmp/nlmapsweb.ini' "$@"
else
    echo 'Warning: No secret ini file nlmapsweb-prod.ini present in repo.'
    ssh "$SSH_USER@$SSH_HOST" bash /tmp/deploy.sh "$@"
fi

