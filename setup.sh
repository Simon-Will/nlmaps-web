export FLASK_APP=application:app
export FLASK_DEBUG=true

POTENTIAL_VENV=~/.virtualenvs/ma-last
if [ -z "$VIRTUAL_ENV" ] && [ -d "$POTENTIAL_VENV" ]; then
    . "$POTENTIAL_VENV/bin/activate"
fi
unset POTENTIAL_VENV
