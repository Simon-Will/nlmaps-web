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
    'n3epsilon.noise.plusv2_web2to1_ratio05_prod.yaml',
    'n3epsilon.noise.plusv2_5515_prod.yaml',
    'n3_ar_ratio05.yaml',
    'n3_arc_ratio05.yaml',
]
CURRENT_MODEL = 'n3_arc_ratio05.yaml'
FALLBACK_MODEL = 'n3.yaml'
