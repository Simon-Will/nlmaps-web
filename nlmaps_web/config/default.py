import os
from pathlib import Path

SECRET_KEY = "asdkjhad321987u21oisnmlk8ud921jpnsöoilawkjdmöod821ue9p2jöolkj"

OVERPASS_URL = 'http://overpass-api.de/api/interpreter'
TAGINFO_URL = 'https://taginfo.openstreetmap.org/'

JOEY_SERVER_URL = 'http://localhost:5050/'

ASSETS_DIR = Path('/home/gorgor/ma')

MODELS = ['foobar.yml', 'barbaz.yml']
CURRENT_MODEL = 'foobar.yml'

ANSWER_COMMAND = [
    'ssh', 'cluster',
    '/opt/slurm/bin/srun -J overpass-query -p main /home/students/will/get_geojson.sh'
]

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(
    (Path(os.path.dirname(__file__)) / '../../nlmaps-web.db').resolve()
)
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

CACHE_DIR = ASSETS_DIR / 'cache'

SESSION_COOKIE_SAMESITE = 'Strict'

# Flask-Login
REMEMBER_COOKIE_SAMESITE = 'Strict'

SECRETS_INI = (ASSETS_DIR / 'nlmaps-web.ini').resolve()

QUESTS = {
    'total': 400,
    'tags': {
        ('wheelchair', 'yes'): 20,
        ('amenity', 'restaurant'): 10,
        ('amenity', 'fast_food'): 10,
        ('amenity', 'cafe'): 10,
    },
    'keys': {
        'shop': 30,
        'leisure': 20,
        'sport': 20,
        'craft': 20,
        'man_made': 10,
        'cuisine': 20,
    },
    'key_prefixes': {
        'diet:': 20,
    }
}

REPLACE_DUPLICATE_NAMES = True
REPLACE_DUPLICATE_NAMES_THRESHOLD = 3

WTF_CSRF_ENABLED = False

# Example for downloadable datasets. name, url_path, license and license_url
# are required fields.
DATASETS = [
    {
        'name': 'NLMaps Web',
        'url_path': '/static/datasets/nlmaps-web.zip',
        'license': 'CC BY-SA',
        'license_url': 'CC BY-SA',
        'original_url': 'https://www.cl.uni-heidelberg.de/statnlpgroup/nlmaps/',
        'comment': 'Collected by different annotators'
    },
    {
        'name': 'NLMaps Web 2',
        'url_path': '/static/datasets/nlmaps-web.zip',
        'license': 'CC BY-SA 4.0',
        'license_url': 'https://creativecommons.org/licenses/by-sa/4.0/',
    }
]
