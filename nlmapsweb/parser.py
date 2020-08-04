import subprocess

from flask import current_app

from mrl import mrl


def parse(query):
    config = current_app.config['NLMAPS_MODEL_CONFIG']
    cwd = current_app.config['JOEYNMT_DIR']
    args = ['python3', '-m', 'joeynmt', 'translate', config]
    proc = subprocess.run(args, cwd=cwd, capture_output=True,
                          input=query, text=True)
    if proc.returncode == 0:
        return proc.stdout
    else:
        print('ERROR')
        print('----')
        print(proc.stdout)
        print('----')
        print(proc.stderr)


def functionalise(lin):
    func = mrl.MRLS['nlmaps']().functionalise(lin)
    return func
