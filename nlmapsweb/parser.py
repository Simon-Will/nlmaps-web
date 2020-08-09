import json
import subprocess

from flask import current_app

from mrl import mrl


def parse(nl_query):
    #config = current_app.config['NLMAPS_MODEL_CONFIG']
    #cwd = current_app.config['JOEYNMT_DIR']
    #args = ['python3', '-m', 'joeynmt', 'translate', config]
    #proc = subprocess.run(args, cwd=cwd, capture_output=True,
    #                      input=query, text=True)
    parse_cmd = current_app.config['PARSE_COMMAND']
    proc = subprocess.run(parse_cmd, capture_output=True,
                          input=nl_query, text=True, check=True)
    return proc.stdout.strip()


def functionalise(lin):
    func = mrl.MRLS['nlmaps']().functionalise(lin.strip())
    return func


def get_geojson_features(mrl):
    answer_cmd = current_app.config['ANSWER_COMMAND']
    proc = subprocess.run(answer_cmd, capture_output=True, input=mrl,
                          text=True, check=True)

    if proc.stdout.startswith('"features": '):
        features = proc.stdout[12:].strip()
        return json.loads(features)
    else:
        return []
