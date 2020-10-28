#!/usr/bin/env python3

from collections import defaultdict, OrderedDict
import re
import sys

import jinja2

PREFIX = """{% extends 'base.html' %}

{% set page = 'osm_tags' %}

{% block content %}
<h2>Available Tags</h2>
"""

BODY = """<ul>
    {% for key, vals in tags.items() %}
    {% for val in vals %}
    <li><a href="https://wiki.openstreetmap.org/Tag:{{ key }}={{ val }}">{{ key }}={{ val }}</a></li>
    {% endfor %}
    {% endfor %}
</ul>
"""

SUFFIX = """{% endblock %}"""


def get_tags_in_mrl(mrl):
    key_val_pairs = []
    for match in re.finditer(r"keyval\('(?P<key>[^']+)','(?P<val>[^']+)'\)",
                             mrl):
        key_val_pairs.append((match.group('key'), match.group('val')))
    return key_val_pairs


def main(filename):
    tags = defaultdict(set)

    with open(filename) as f:
        i = 0
        for line in f:
            for key, val in get_tags_in_mrl(line):
                if key != 'name':
                    tags[key].add(val)

    ordered_tags = OrderedDict()
    for key in sorted(tags):
        ordered_tags[key] = sorted(tags[key])

    body_template = jinja2.Template(BODY, trim_blocks=True, lstrip_blocks=True)
    body = body_template.render(tags=ordered_tags)

    print(PREFIX)
    print(body)
    print(SUFFIX)
    
    #all_tags = []
    #for key, vals in tags.items():
    #    for val in vals:
    #        all_tags.append('{}={}'.format(key, val))

    #for tag in sorted(all_tags):
    #    print(tag)


if __name__ == '__main__':
    main(sys.argv[1])
