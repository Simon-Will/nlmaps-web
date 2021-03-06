"""Data and functions for the NLMaps Web tutorial.

The tutorial consists of chapters, each of which is completed by sending the
correct feedback for a specific NL query. The normal NL and feedback handling
in `query.py` view recognizes if one of these specific NL queries is sent and
handles it by using the `tutorial_dummy_parser` and `tutorial_dummy_saver`
below. The normal flow is then replaced by using the data from
NL_TO_INSTRUCTIONS.

A user’s progress in the tutorial is stored in the user row in the database if
the user is authenticated. Otherwise it is stored in a browser session.
"""

import time

from flask_login import current_user
from flask import session

from nlmaps_web.app import db
from nlmaps_web.processing.converting import functionalise, linearise
from nlmaps_web.processing.parsing import ParseResult

CHAPTERS = [
    'Introduction',
    'Correcting a Tag',
    'Querying Named Places and QType',
    'Querying around Named Places',
    'Querying the Closest Thing',
    'Querying the Distance to the Closest Thing',
    'Querying the Distance between Two Places',
    'Finish',
]

NL_TO_INSTRUCTIONS = {
    'How many bakeries are there in Hamburg?': {
        'chapter': 1,
        'parsed_mrl': "query(area(keyval('name','Hamburg')),nwr(keyval('shop','bakery')),qtype(count))",
        'feedback_mrl':  "query(area(keyval('name','Hamburg')),nwr(keyval('shop','bakery')),qtype(count))",
        'tips': ['You don’t need to do anything but click “That’s Correct!”.']
    },
    'Where in Stratford-upon-Avon can my kids go to play?': {
        'chapter': 2,
        'parsed_mrl': "query(area(keyval('name','Stratford-upon-Avon')),nwr(keyval('amenity','play')),qtype(latlong))",
        'feedback_mrl': "query(area(keyval('name','Stratford-upon-Avon')),nwr(keyval('leisure','playground')),qtype(latlong))",
        'tips': ['Click “Adjust”, change the tag to the tag for a playground and resubmit.']
    },
    'When can we visit the Guggenheim Museum in New York City?': {
        'chapter': 3,
        'parsed_mrl': "query(area(keyval('name','New York City')),nwr(keyval('name','Guggenheim Museum')),qtype(latlong))",
        'feedback_mrl': "query(area(keyval('name','New York City')),nwr(keyval('name','Guggenheim Museum')),qtype(findkey('opening_hours')))",
        'tips': ['Change the qtype such that NLMaps Web will look up the opening hours.']
    },
    'Are there any hotels that we can walk to from the Taj Mahal?':{
        'chapter': 4,
        'parsed_mrl': "query(around(center(nwr(keyval('name','Taj Mahal'))),search(nwr(keyval('tourism','hotel'))),maxdist(3000)),qtype(findkey('website')))",
        'feedback_mrl': "query(around(center(nwr(keyval('name','Taj Mahal'))),search(nwr(keyval('tourism','hotel'))),maxdist(WALKING_DIST)),qtype(least(topx(1))))",
        'tips': [
            'Change the maximum distance to walking distance, which is a *named* distance.',
            'Change the qtype such that it will tell you if there is at least one (“least(topx(1))”) result'
        ]
    },
    'Name the synagogue that is closest to the Országház in Budapest!': {
        'chapter': 5,
        'parsed_mrl':  "query(around(center(area(keyval('name','Budapest')),nwr(keyval('name','Országház'))),search(nwr(keyval('amenity','place_of_worship'))),maxdist(DIST_INTOWN)),qtype(latlong))",
        'feedback_mrl':  "query(around(center(area(keyval('name','Budapest')),nwr(keyval('name','Országház'))),search(nwr(keyval('amenity','place_of_worship'),keyval('religion','jewish'))),maxdist(DIST_INTOWN),topx(1)),qtype(findkey('name')))",
        'tips': [
            'Add a tag such that it will find objects that are places of worship AND jewish.',
            'Restrict the results to the closest object.'
            'Change the qtype such that it will extract objects’ names.'
        ]
    },
    'How far is it from Rotes Rathaus in Berlin to the next restaurant serving some vegetarian food?': {
        'chapter': 6,
        'parsed_mrl': "dist(query(around(center(area(keyval('name','Berlin')),nwr(keyval('name','Rotes Rathaus'))),search(nwr(keyval('amenity','regetarian'))),maxdist(DIST_INTOWN),topx(1)),qtype(latlong)))",
        'feedback_mrl': "dist(query(around(center(area(keyval('name','Berlin')),nwr(keyval('name','Rotes Rathaus'))),search(nwr(keyval('amenity','restaurant'),keyval('diet:vegetarian',or('only','yes')))),maxdist(DIST_INTOWN),topx(1)),qtype(latlong)))",
        'tips': ['Change the tags. We want to find a restaurant that serves only vegetarian food OR at least some vegetarian food.']
    },
    'Tell me the distance between Empire State Building in New York City and Bratislavský hrad': {
        'chapter': 7,
        'parsed_mrl': "dist(query(around(center(area(keyval('name','New York City')),nwr(keyval('name','Empire State Building'))),search(nwr(keyval('name','Bratislavský hrad'))),maxdist(DIST_INTOWN),topx(1)),qtype(latlong)))",
        'feedback_mrl': "dist(query(area(keyval('name','New York City')),nwr(keyval('name','Empire State Building')),qtype(latlong)),query(nwr(keyval('name','Bratislavský hrad')),qtype(latlong)))",
        'tips': [
            'Use the drop down menu to change the Question Class to find the distance between two objects.',
            'Search for the Empire State Building in New York City and don’t restrict the area for Bratislavský hrad.',
            'Order is important. What is named first in the NL query should be first in the MRL query.',
        ]
    },
}


def tutorial_dummy_parser(nl):
    """Return the premade MRL for the given NL.

    Most of the MRLs above contain a number of errors that the user has to fix.
    """
    instructions = NL_TO_INSTRUCTIONS.get(nl)
    if instructions:
        mrl = instructions['parsed_mrl']
        lin = linearise(mrl)
        time.sleep(2)
        return ParseResult(success=True, nl=nl, lin=lin, mrl=mrl,
                           model='tutorial')
    return None


def get_user_chapter():
    """Return the current chapter the user is at.

    This is taken from the database if the user is authenticated, else from the
    session.
    """
    if current_user.is_authenticated:
        return current_user.tutorial_chapter
    return session.get('tutorial_chapter', 0)


def set_user_chapter(chapter_finished):
    """Set the user chapter to the chapter after the finished one.

    Set in database for authenticated users, in the session for others.
    """
    if chapter_finished == len(CHAPTERS) - 1:
        # Tutorial is finished. Set to -1.
        chapter_to_set = -1
    else:
        chapter_to_set = chapter_finished + 1

    if current_user.is_authenticated:
        if chapter_to_set == -1 or current_user.tutorial_chapter < chapter_to_set:
            current_user.tutorial_chapter = chapter_to_set
            db.session.add(current_user)
            db.session.commit()
    else:
        session['tutorial_chapter'] = chapter_to_set


def tutorial_dummy_saver(feedback):
    """Tell the user if the feedback they gave was the one that was expected.

    This function does not save any feedback. Instead, it gives the user tips
    on how to give the expected feedback if the feedback was not the one that
    was expected. Otherwise (i.e. the feedback was the expected one), the user
    is redirected to the next chapter in the tutorial.
    """
    instructions = NL_TO_INSTRUCTIONS.get(feedback['nl'])
    if instructions:
        mrl = functionalise(feedback['correct_lin'])
        if mrl == instructions['feedback_mrl']:
            chapter_finished = instructions['chapter']
            set_user_chapter(chapter_finished)
            feedback['id'] = 0
            feedback['chapter_finished'] = chapter_finished
            return feedback, 200

        feedback['error'] = 'Wrong tutorial feedback: {}'.format(mrl)
        feedback['tips'] = instructions.get('tips')
        return feedback, 400

    feedback['error'] = ('The NL {!r} does not occur in the tutorial.'
                         .format(feedback['nl']))
    return feedback, 400
