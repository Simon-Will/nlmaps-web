import os
from pathlib import Path

DEBUG = False

ASSETS_DIR = Path(os.environ['ASSETS'])
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(
    (ASSETS_DIR / 'nlmapsweb.db').resolve()
)

with open(ASSETS_DIR / 'secret_key.txt') as f:
    SECRET_KEY = f.read().strip()

MODELS = [
    'will_nlmaps_3gamma.noise.plusv2_online_incorrect_bs10_ratio0.5.yaml'
]
CURRENT_MODEL = 'will_nlmaps_3gamma.noise.plusv2_online_incorrect_bs10_ratio0.5.yaml'
