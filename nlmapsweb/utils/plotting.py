import base64
import io

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_tagged_percentages(tag_counts, total, width=0.35):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    sorted_tags = sorted(tag_counts.keys())
    percentages_tagged = [tag_counts[tag] / total for tag in sorted_tags]
    percentages_left = [1 - perc for perc in percentages_tagged]
    ind = range(len(sorted_tags))

    plt_tagged, *_ = ax.barh(ind, percentages_tagged, width, color='red')
    ax.barh(ind, percentages_left, width, left=percentages_tagged,
            color='lightgray')

    #sorted_tags = [chr(0x61 + i) for i in range(len(sorted_tags))]
    ax.set_title('Percentage of Tagged Instances by Tag')
    ax.set_xticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel('Percentage')
    ax.set_yticks(ind)
    ax.set_yticklabels(sorted_tags, fontsize=8)
    fig.subplots_adjust(left=0.30)

    #ax.legend([plt_tagged], ['Percentage Tagged'])

    return fig


def fig_to_base64(fig, format='jpg'):
    bio = io.BytesIO()
    fig.savefig(bio, format=format)
    bio.seek(0)
    b64 = base64.b64encode(bio.read()).decode('utf-8')
    return b64
