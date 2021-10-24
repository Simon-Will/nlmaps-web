from copy import deepcopy
from pathlib import Path
import random
import re

from flask import current_app
from flask_login import current_user

from nlmaps_web.models.name_occurrences import NameOccurrence
from nlmaps_web.processing.converting import (
    features_to_mrl, linearise, mrl_to_features)

AREAS = None
POIS = None


def read_data_file(basename):
    path = (Path(__file__) / '../../data' / basename).resolve()
    with open(path) as f:
        lines = [line.strip() for line in f]
    return lines


def get_area():
    global AREAS
    if AREAS is None:
        AREAS = read_data_file('areas.txt')
    return random.choice(AREAS)


def get_poi():
    global POIS
    if POIS is None:
        POIS = read_data_file('pois.txt')
    return random.choice(POIS)


def count_occurrences(name, nl):
    return len(re.findall(re.escape(name), nl))


def replace_names_in_nwr(nwr_features, nl, user_id, threshold):
    parts = []
    for feat in nwr_features:
        if feat[0] in ['or', 'and'] and isinstance(feat[1], (list, tuple)):
            sub_features, nl = replace_names_in_nwr(feat[1:], nl, user_id,
                                                    threshold)
            if not sub_features:
                return None, nl
            parts.append((feat[0], *sub_features))
        elif (len(feat) == 2 and isinstance(feat[1], (list, tuple))
              and feat[1][0] == 'or'):
            if feat[0] == 'name':
                old_names = list(set(feat[1][1:]))
                occs_per_name = [count_occurrences(name, nl)
                                 for name in old_names]
                if any(occs != 1 for occs in occs_per_name):
                    return None, nl
                new_names = []
                for old_name in old_names:
                    if NameOccurrence.get_count(old_name,
                                                user_id) >= threshold:
                        new_names.append(get_poi())
                    else:
                        new_names.append(old_name)
                for old_name, new_name in zip(old_names, new_names):
                    nl = nl.replace(old_name, new_name)
                parts.append(('name', ('or', *new_names)))
            else:
                parts.append(feat)
        elif len(feat) == 2 and all(isinstance(f, str) for f in feat):
            if feat[0] == 'name':
                old_name = feat[1]
                if NameOccurrence.get_count(old_name, user_id) >= threshold:
                    occs = count_occurrences(old_name, nl)
                    if occs != 1:
                        return None, nl
                    new_name = get_poi()
                    nl = nl.replace(old_name, new_name)
                    parts.append(('name', new_name))
                else:
                    parts.append((feat[0], feat[1]))
            else:
                parts.append((feat[0], feat[1]))
        else:
            raise ValueError('Unexpected feature part: {}'.format(feat))

    return tuple(parts), nl


def replace_names_in_features(features, nl, user_id, area_replaced=False):
    fail_value = (None, None, False)

    features = deepcopy(features)
    threshold = current_app.config.get('REPLACE_DUPLICATE_NAMES_THRESHOLD', 3)

    if 'area' in features:
        area = features['area']
        if NameOccurrence.get_count(area, user_id) >= threshold:
            new_area = get_area()
            occs = count_occurrences(area, nl)
            if occs == 0 and not area_replaced:
                current_app.logger.info('Not replacing area ({} occurrences).'
                                        .format(occs))
                return fail_value
            if occs > 2:
                current_app.logger.info('Not replacing area ({} occurrences).'
                                        .format(occs))
                return fail_value
            features['area'] = new_area
            nl = nl.replace(area, new_area)
            area_replaced = True

    features['target_nwr'], nl = replace_names_in_nwr(
        features['target_nwr'], nl, user_id, threshold)
    if not features['target_nwr']:
        current_app.logger.info('Failed to replace target_nwr')
        return fail_value

    if 'center_nwr' in features:
        features['center_nwr'], nl = replace_names_in_nwr(
            features['center_nwr'], nl, user_id, threshold)
        if not features['center_nwr']:
            current_app.logger.info('Failed to replace center_nwr')
            return fail_value

    return features, nl, area_replaced


def replace_feedback(feedback, correct_mrl, user_id=None):
    if not user_id:
        if current_user.is_authenticated:
            user_id = current_user.id
        else:
            return None, None

    if not correct_mrl or not feedback.get('correct_lin'):
        return None, None

    if correct_mrl:
        features = mrl_to_features(correct_mrl)
    if not features:
        return None, None

    if 'sub' in features:
        new_features_0, new_nl, area_replaced = replace_names_in_features(
            features['sub'][0], feedback['nl'], user_id)
        features['sub'][0] = new_features_0
        if len(features['sub']) > 1:
            new_features_1, new_nl, _ = replace_names_in_features(
                features['sub'][1], new_nl, user_id, area_replaced)
            features['sub'][1] = new_features_1
    else:
        features, new_nl, _ = replace_names_in_features(features, feedback['nl'], user_id)

    if new_nl == feedback['nl']:
        return None, None

    mrl = features_to_mrl(features)
    if mrl:
        lin = linearise(mrl)
        new_feedback = deepcopy(feedback)
        new_feedback['nl'] = new_nl
        new_feedback['correct_lin'] = lin
        new_feedback.pop('id', None)
        new_feedback.pop('created', None)
        return new_feedback, mrl

    return None, None


def get_names_from_nwr(nwr_features):
    names = set()
    for feat in nwr_features:
        if feat[0] in ['or', 'and'] and isinstance(feat[1], (list, tuple)):
            names.update(get_names_from_nwr(feat[1:]))
        elif (len(feat) == 2 and isinstance(feat[1], (list, tuple))
              and feat[1][0] == 'or'):
            if feat[0] == 'name':
                names.update(feat[1][1:])
        elif len(feat) == 2 and all(isinstance(f, str) for f in feat):
            if feat[0] == 'name':
                names.add(feat[1])
        else:
            raise ValueError('Unexpected feature part: {}'.format(feat))

    return names


def get_names_from_non_dist_features(features):
    names = set()
    if 'area' in features:
        names.add(features['area'])

    names.update(get_names_from_nwr(features['target_nwr']))
    if 'center_nwr' in features:
        names.update(get_names_from_nwr(features['center_nwr']))

    return names


def increment_name_occurrences(mrl, user_id=None):
    if not user_id:
        if current_user.is_authenticated:
            user_id = current_user.id
        else:
            return None

    if mrl:
        features = mrl_to_features(mrl)
        if not features:
            return None
    else:
        return None

    if 'sub' in features:
        names = {name for feats in features['sub']
                 for name in get_names_from_non_dist_features(feats)}
    else:
        names = get_names_from_non_dist_features(features)

    for name in names:
        NameOccurrence.increment(name, user_id)
