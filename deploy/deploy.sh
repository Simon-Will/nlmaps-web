#!/usr/bin/env bash

set -e

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
    if [ -d "$NLMAPS_WEB_REPO" ]; then
        pushd "$NLMAPS_WEB_REPO"
        git pull origin master
        popd
    else
        git clone "$NLMAPS_WEB_REMOTE" "$NLMAPS_WEB_REPO"
    fi

    if [ -d "$NLMAPS_TOOLS_REPO" ]; then
        pushd "$NLMAPS_TOOLS_REPO"
        git pull origin master
        popd
    else
        git clone "$NLMAPS_TOOLS_REMOTE" "$NLMAPS_TOOLS_REPO"
    fi
}

python_install() {
    if [ "$REINSTALL" = 1 ] || ! [ -d "$ASSETS/venv" ]; then
        rm -rf "$ASSETS/venv"
        log 'Making virtual environment'
        python3 -m venv "$ASSETS/venv"

        log 'Activating virtual environment'
        . "$ASSETS/venv/bin/activate"

        log 'Installing nlmaps-web'
        pip3 install -U pip wheel
        pip3 install -U setuptools uwsgi
        pip3 install -e "$NLMAPS_TOOLS_REPO"
        pip3 install -e "$NLMAPS_WEB_REPO"
    else
        log 'Activating virtual environment'
        . "$ASSETS/venv/bin/activate"
    fi
}

external_js_install() {
    local openlayers_url='https://github.com/openlayers/openlayers/releases/download/v6.5.0/v6.5.0-dist.zip'
    local libdir="$NLMAPS_WEB_REPO/nlmaps_web/static/lib"
    if [ "$REINSTALL" = 1 ] || ! [ -d "$libdir" ]; then
        log 'Downloading and installing OpenLayers'
        wget "$openlayers_url" -O /tmp/ol-dist.zip
        unzip -d /tmp/ol-dist /tmp/ol-dist.zip

        mkdir -p "$libdir/ol"
        find /tmp/ol-dist -type f -exec mv {} "$libdir/ol" \;
    fi
}

ensure_secret_key() {
    if ! [ -f "$ASSETS/secret_key.txt" ]; then
        log 'Creating secret key'
        tr -dc A-Za-z0-9 </dev/urandom | head -c 50 >"$ASSETS/secret_key.txt"
        chmod 600 "$ASSETS/secret_key.txt"
    fi
}

install_nlmaps_web_ini() {
    if [ -f "$NLMAPS_WEB_INI" ]; then
        log 'Installing nlmaps-web.ini'
        cp "$NLMAPS_WEB_INI" "$ASSETS/nlmaps-web.ini"
    fi
}

create_setup_sh() {
    cat >"$ASSETS/setup.sh" <<EOT
export FLASK_APP=nlmaps_web.fullapp
export FLASK_ENV=production
export ASSETS='$ASSETS'
. '$ASSETS/venv/bin/activate'
EOT
}

migrate() {
    log 'Running migrations'
    pushd "$NLMAPS_WEB_REPO"
    flask db upgrade
    popd
}

start_app() {
    log 'Starting app'
    bash "$NLMAPS_WEB_REPO/deploy/run_uwsgi.sh"
}

main() {
    REINSTALL=0
    NLMAPS_WEB_PORT=8000
    ASSETS="$HOME/nlmaps-web-assets"
    NLMAPS_WEB_INI=''

    while getopts ':rp:a:i:' opt; do
        case $opt in
            r)
                REINSTALL=1
                ;;
            p)
                NLMAPS_WEB_PORT="$OPTARG"
                ;;
            a)
                ASSETS="$OPTARG"
                ;;
            i)
                NLMAPS_WEB_INI="$OPTARG"
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

    export NLMAPS_WEB_REPO=${1:-$HOME/nlmaps-web}
    NLMAPS_TOOLS_REPO=${2:-$HOME/nlmaps-tools}
    NLMAPS_WEB_REMOTE='git@github.com:Simon-Will/nlmaps-web.git'
    NLMAPS_TOOLS_REMOTE='git@github.com:Simon-Will/nlmaps-tools.git'

    export ASSETS
    export NLMAPS_WEB_PORT
    export FLASK_APP=nlmaps_web.fullapp:app
    export FLASK_ENV=production

    check
    mkdir -p "$ASSETS"
    repo_sync
    python_install
    external_js_install
    ensure_secret_key
    install_nlmaps_web_ini
    create_setup_sh
    migrate
    start_app
}

main "$@"
