#!/usr/bin/env python3

import argparse
from collections import OrderedDict
import pickle
import random

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline


def fit_tf_idf_pipeline(dataset):
    pipeline = Pipeline([('count', CountVectorizer()),
                         ('tfidf', TfidfTransformer())])
    pipeline.fit(dataset)
    return pipeline


def load_tf_idf_pipeline(pickle_file):
    try:
        with open(pickle_file, 'rb') as f:
            pipeline = pickle.load(f)
    except (FileNotFoundError, pickle.UnpicklingError):
        pipeline = None

    return pipeline


def get_tf_idf_scores(pipeline, sentence):
    tf_idf = pipeline.transform([sentence])
    feature_names = pipeline['count'].get_feature_names()
    processed_tokens = [feature_names[idx] for idx in tf_idf.indices]

    tokenizer = pipeline['count'].build_tokenizer()
    all_tokens = set(tokenizer(sentence))
    unprocessed_tokens = list(all_tokens.difference(processed_tokens))
    processed_tokens.extend(token.lower() for token in unprocessed_tokens)
    data = list(tf_idf.data)
    data.extend([1.0] * len(unprocessed_tokens))

    return OrderedDict(sorted(
        zip(processed_tokens, data),
        key=lambda tup: tup[1],
        reverse=True
    ))


def main(dataset_file, test_sentence=None, save_file=None):
    with open(dataset_file) as f:
        lines = [line.strip() for line in f]

    pipeline = fit_tf_idf_pipeline(lines)

    if test_sentence:
        tf_idf_scores = get_tf_idf_scores(pipeline, test_sentence)
        print(tf_idf_scores)
    else:
        random_lines = random.choices(lines, k=20)
        for line in random_lines:
            tf_idf_scores = get_tf_idf_scores(pipeline, line)
            print(line)
            print(', '.join(
                '{}: {}'.format(token, score)
                for token, score in tf_idf_scores.items()
            ))
            print()

    if save_file:
        with open(save_file, 'wb') as f:
            pickle.dump(pipeline, f)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_file')
    parser.add_argument('--test-sentence', '-t', help='Sentence to test on.')
    parser.add_argument('--save-file', '-s',
                        help='File to save the pipeline in')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    ARGS = parse_args()
    main(**vars(ARGS))
