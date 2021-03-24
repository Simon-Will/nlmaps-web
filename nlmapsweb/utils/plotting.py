import base64
from collections import defaultdict
import io

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_validations(validations):
    validations_by_label = defaultdict(list)
    for validation in validations:
        validations_by_label[validation['label']].append(validation)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for label, vals in validations_by_label.items():
        artist = ax.plot(
            [val['created'] for val in vals],
            [val['accuracy'] for val in vals],
            label=label
        )

    ax.legend()
    ax.set_title('Evalution Results over Time')
    ax.set_ylim((0.0, 1.0))

    return fig


def fig_to_base64(fig, format='jpg'):
    bio = io.BytesIO()
    fig.savefig(bio, format=format)
    bio.seek(0)
    b64 = base64.b64encode(bio.read()).decode('utf-8')
    return b64
