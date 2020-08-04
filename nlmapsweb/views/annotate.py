import re

from flask import current_app, render_template

from nlmapsweb.forms.query import QueryForm
from nlmapsweb.parser import functionalise, parse
from nlmapsweb.taginfo import check_key_val_pair


def get_key_val_pairs(mrl):
    key_val_pairs = []
    for match in re.finditer(r"keyval\('(?P<key>[^']+)','(?P<val>[^']+)'\)",
                             mrl):
        key_val_pairs.append((match.group('key'), match.group('val')))
    return key_val_pairs


@current_app.route('/annotate', methods=['GET', 'POST'])
def annotate():
    form = QueryForm()
    query = None
    lin = None
    func = None
    alternatives = None

    if form.validate_on_submit():
        query = form.query.data
        lin = parse(query)
        func = functionalise(lin)
        print(lin)
        print(func)

        alternatives = {}
        key_val_pairs = get_key_val_pairs(func)
        for key, val in key_val_pairs:
            alternatives[(key, val)] = check_key_val_pair(key, val)

    return render_template('annotate.html', form=form, query=query, lin=lin,
                           func=func, alternatives=alternatives)
