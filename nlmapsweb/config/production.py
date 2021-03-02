import os
from pathlib import Path

DEBUG = False

ASSETS_DIR = Path(os.environ['ASSETS'])

SECRETS_INI = (ASSETS_DIR / 'nlmapsweb.ini').resolve()
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(
    (ASSETS_DIR / 'nlmapsweb.db').resolve()
)
CACHE_DIR = ASSETS_DIR / 'cache'

with open(ASSETS_DIR / 'secret_key.txt') as f:
    SECRET_KEY = f.read().strip()

MODELS = [
    'will_nlmaps_3delta.noise.plusv2_lin_char_legacy.yaml',
    'will_nlmaps_3delta.noise.plusv2_web2to1_ratio05_fixed.yaml',
    'will_nlmaps_3delta.noise.plusv2_web2to1_ratio05_pilot.yaml',
]
CURRENT_MODEL = 'will_nlmaps_3delta.noise.plusv2_web2to1_ratio05_pilot.yaml'

