#!/usr/bin/env bash

SSH_USER=nlmaps
SSH_HOST=nlmaps

THIS_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DEPLOY_SCRIPT="$THIS_DIR/deploy.sh"

scp "$DEPLOY_SCRIPT" "$SSH_USER@$SSH_HOST:/tmp/deploy.sh"
ssh "$SSH_USER@$SSH_HOST" bash /tmp/deploy.sh "$@"
