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
    'n3_arc_ratio05_prod.yaml',
]
CURRENT_MODEL = 'n3_arc_ratio05_prod.yaml'
FALLBACK_MODEL = 'n3.yaml'

DATASETS = [
    {
        'name': 'NLMaps 2.1',
        'url_path': '/static/datasets/nlmaps_v2.1.zip',
        'license': 'CC BY-NC-SA 4.0',
        'license_url':  'https://creativecommons.org/licenses/by-nc-sa/4.0/',
        'original_url': 'https://www.cl.uni-heidelberg.de/statnlpgroup/nlmaps/',
        'comment': 'Modification of NLMaps v2, published by Carolin Lawrence and Stefan Riezler.',
    },
    {
        'name': 'NLMaps 3a',
        'url_path': '/static/datasets/nlmaps_v3a.zip',
        'license': 'CC BY-SA 4.0',
        'license_url': 'https://creativecommons.org/licenses/by-sa/4.0/',
    },
    {
        'name': 'NLMaps 3b',
        'url_path': '/static/datasets/nlmaps_v3b.zip',
        'license': 'CC BY-SA 4.0',
        'license_url': 'https://creativecommons.org/licenses/by-sa/4.0/',
    },
    {
        'name': 'NLMaps 3',
        'url_path': '/static/datasets/nlmaps_v3.zip',
        'license': 'CC BY-NC-SA 4.0',
        'license_url':  'https://creativecommons.org/licenses/by-nc-sa/4.0/',
    },
    {
        'name': 'NLMaps 3 (no noise)',
        'url_path': '/static/datasets/nlmaps_v3_no_noise.zip',
        'license': 'CC BY-NC-SA 4.0',
        'license_url':  'https://creativecommons.org/licenses/by-nc-sa/4.0/',
    },
    {
        'name': 'NLMaps 4 (raw)',
        'url_path': '/static/datasets/nlmaps_v4_raw.zip',
        'license': 'CC BY-SA 4.0',
        'license_url':  'https://creativecommons.org/licenses/by-sa/4.0/',
    },
    {
        'name': 'NLMaps 4',
        'url_path': '/static/datasets/nlmaps_v4.zip',
        'license': 'CC BY-SA 4.0',
        'license_url':  'https://creativecommons.org/licenses/by-sa/4.0/',
    },
]
