#!/usr/bin/env bash

set -eo pipefail

err() {
    echo "$@" >&2
}

log() {
    echo
    echo "=== $* ==="
}

check() {
    if [ "$USER" != nlmaps ]; then
        err "User should be nlmaps, but is $USER"
        exit 2
    fi
}

repo_sync() {
    log 'Pulling changes from repositories'
    if [ -d "$NLMAPSWEB_REPO" ]; then
        pushd "$NLMAPSWEB_REPO"
        git pull origin master
        popd
    else
        git clone "$NLMAPSWEB_REMOTE" "$NLMAPSWEB_REPO"
    fi

    if [ -d "$NLMAPSTOOLS_REPO" ]; then
        pushd "$NLMAPSTOOLS_REPO"
        git pull origin master
        popd
    else
        git clone "$NLMAPSTOOLS_REMOTE" "$NLMAPSTOOLS_REPO"
    fi
}

python_install() {
    if [ "$REINSTALL" = 1 ] || ! [ -d "$ASSETS/venv" ]; then
        rm -rf "$ASSETS/venv"
        log 'Making virtual environment'
        python3 -m venv "$ASSETS/venv"

        log 'Activating virtual environment'
        . "$ASSETS/venv/bin/activate"

        log 'Installing nlmapsweb'
        pip3 install -U pip wheel
        pip3 install -U setuptools uwsgi
        pip3 install -e "$NLMAPSTOOLS_REPO"
        pip3 install -e "$NLMAPSWEB_REPO"
    else
        log 'Activating virtual environment'
        . "$ASSETS/venv/bin/activate"
    fi
}

ensure_secret_key() {
    if ! [ -f "$ASSETS/secret_key.txt" ]; then
        log 'Creating secret key'
        tr -dc A-Za-z0-9 </dev/urandom | head -c 50 >"$ASSETS/secret_key.txt"
        chmod 600 "$ASSETS/secret_key.txt"
    fi
}

migrate() {
    log 'Running migrations'
    flask db upgrade
}

start_app() {
    log 'Starting app'
    bash "$NLMAPSWEB_REPO/deploy/run_uwsgi.sh"
}

main() {
    REINSTALL=0
    NLMAPSWEB_PORT=8000
    ASSETS="$HOME/assets"

    while getopts ':rp:a:' opt; do
        case $opt in
            r)
                REINSTALL=1
                ;;
            p)
                NLMAPSWEB_PORT="$OPTARG"
                ;;
            a)
                ASSETS="$OPTARG"
                ;;
            \?)
                err_with_help "Invalid option: -$OPTARG"
                ;;
            :)
                err_with_help "Option -$OPTARG requires an argument"
                ;;
        esac
    done

    shift $((OPTIND-1))

    export NLMAPSWEB_REPO=${1:-$HOME/nlmapsweb}
    NLMAPSTOOLS_REPO=${2:-$HOME/nlmaps-tools}
    NLMAPSWEB_REMOTE='git@gitlab.cl.uni-heidelberg.de:will/nlmapsweb.git'
    NLMAPSTOOLS_REMOTE='git@gitlab.cl.uni-heidelberg.de:will/nlmaps-tools.git'

    export ASSETS
    export NLMAPSWEB_PORT
    export FLASK_APP=nlmapsweb.fullapp:app
    export FLASK_ENV=production

    check
    mkdir -p "$ASSETS"
    repo_sync
    python_install
    ensure_secret_key
    migrate
    start_app
}

main "$@"
