from collections import defaultdict

import click
from flask import current_app

import nlmaps_web.mt_server as mt_server
from nlmaps_web.views.feedback import FeedbackPiece
from nlmaps_web.processing.converting import mrl_to_features
from nlmaps_web.processing.custom_tag_suggestions import extract_suggested_tags
from nlmaps_web.processing.diagnosing import DiagnoseResult
from nlmaps_web.processing.tagfinder import (extract_tagfinder_tags,
                                            get_tagfinder_info_by_scores)


def tag_help_eval():
    """Evaluate the tag help"""
    pass


def eval():
    "Evaluate"
    filters = {'model': current_app.config['CURRENT_MODEL']}
    response = mt_server.post('query_feedback', json=filters)
    feedback = [FeedbackPiece(**data) for data in response.json()]

    by_nl = {piece.nl: {'fb': piece}
             for piece in feedback if piece.correct_mrl}

    expected_tags_count = 0
    suggested_tags_count = 0
    found_tags_count = 0
    non_found_tags = defaultdict(lambda: 0)
    for nl, info in by_nl.items():
        mrl = info['fb'].correct_mrl
        if mrl:
            diagnose = DiagnoseResult.from_nl_mrl(nl, mrl)
            expected_tags = {tuple(taginfo[0]) for taginfo in diagnose.taginfo}
            suggested_tags = extract_suggested_tags(diagnose.custom_suggestions)
            tagfinder_info = get_tagfinder_info_by_scores(
                diagnose.tf_idf_scores)
            if tagfinder_info:
                suggested_tags.update(extract_tagfinder_tags(tagfinder_info))
            found_tags = expected_tags.intersection(suggested_tags)
            #print(expected_tags)
            #print(suggested_tags)
            #print(found_tags)
            #print(expected_tags.difference(suggested_tags))
            #print('---')

            expected_tags_count += len(expected_tags)
            suggested_tags_count += len(suggested_tags)
            found_tags_count += len(found_tags)

            for tag in expected_tags.difference(suggested_tags):
                non_found_tags[tag] += 1

    recall = (found_tags_count / expected_tags_count
              if expected_tags_count else None)
    precision = (found_tags_count / suggested_tags_count
                 if suggested_tags_count else None)

    report_template = '''
Expected Tags: {expected_count}
Suggested Tags: {suggested_count}
Found Tags: {found_count}

Recall: {recall}
Precision: {precision}

Non-Found Tags with non-found count:
{non_found_tags}'''
    report = report_template.format(
        expected_count=expected_tags_count,
        suggested_count=suggested_tags_count,
        found_count=found_tags_count,
        recall=recall,
        precision=precision,
        non_found_tags=', '.join(
            '{}={}: {}'.format(tag[0], tag[1], count)
            for tag, count in sorted(non_found_tags.items(),
                                     key=lambda item: item[1],
                                     reverse=True)
        )
    )
    print(report)


spec = {
    'group': tag_help_eval,
    'commands': [eval]
}
