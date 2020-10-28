"""Default config for all environments

All configurations which are relevant for using and running the web app
can be defined here. These settings will be loaded first and can be
overwritten by environment specific configurations. The logic is defined
in `app.py` and is as follows:

1. Read DEFAULTS (for all environments), this file here
2. Read ENVIRONMENT SPECIFIC CONFIG FILES, provided in same folder
3. Read sensitive values given in ENVIRONMENT VARIABLE
"""

import os
from pathlib import Path

DEBUG = False

SECRET_KEY = "asdkjhad321987u21oisnmlk8ud921jpnsöoilawkjdmöod821ue9p2jöolkj"

MA_DIR = Path('/home/gorgor/ma')
#JOEYNMT_DIR = MA_DIR / 'joeynmt'
#NLMAPS_MODEL_CONFIG = JOEYNMT_DIR / 'configs/staniek_nlmaps_lin_char_upper2_cpu.yaml'

MOST_COMMON_TAGS = MA_DIR / 'data/most_common_tags/most_common_tags.json'

PARSE_COMMANDS = {
    'staniek_nlmaps_lin_char': [
        'ssh', 'last', (
            'cd /home/students/will/public/ma/joeynmt;'
            ' /home/students/will/.virtualenvs/ma-last/bin/python3 -m joeynmt translate'
            ' /home/students/will/public/ma/joeynmt/configs/staniek_nlmaps_lin_char_upper2_cpu.yaml'
        )
    ],
    'will_nlmaps_3beta.noise.plusv2_lin_char': [
        'ssh', 'last', (
            'cd /home/students/will/public/ma/joeynmt;'
            ' /home/students/will/.virtualenvs/ma-last/bin/python3 -m joeynmt translate'
            ' /home/students/will/public/ma/joeynmt/configs/will_nlmaps_3beta.noise.plusv2_lin_char_cpu.yaml'
        )
    ]
}
CURRENT_MODEL = 'staniek_nlmaps_lin_char'

ANSWER_COMMAND = [
    'ssh', 'cluster',
    '/opt/slurm/bin/srun -J overpass-query -p main /home/students/will/get_geojson.sh'
]

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(
    (Path(os.path.dirname(__file__)) / '../nlmapsweb.db').resolve()
)
SQLALCHEMY_ECHO = False

OVERPASS_URL='http://overpass-api.de/api/interpreter'
