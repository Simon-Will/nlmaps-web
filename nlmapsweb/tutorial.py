import time

from flask_login import current_user
from flask import session

from nlmapsweb.app import db
from nlmapsweb.processing.converting import functionalise, linearise
from nlmapsweb.processing.parsing import ParseResult

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
        'feedback_mrl':  "query(area(keyval('name','Hamburg')),nwr(keyval('shop','bakery')),qtype(count))"
    },
    'Where in Stratford-upon-Avon can my kids go to play?': {
        'chapter': 2,
        'parsed_mrl': "query(area(keyval('name','Stratford-upon-Avon')),nwr(keyval('amenity','play')),qtype(latlong))",
        'feedback_mrl': "query(area(keyval('name','Stratford-upon-Avon')),nwr(keyval('leisure','playground')),qtype(latlong))",
    },
    'When can we visit the Guggenheim Museum in New York City?': {
        'chapter': 3,
        'parsed_mrl': "query(area(keyval('name','New York City')),nwr(keyval('name','Guggenheim Museum')),qtype(latlong))",
        'feedback_mrl': "query(area(keyval('name','New York City')),nwr(keyval('name','Guggenheim Museum')),qtype(findkey('opening_hours')))"
    },
    'Are there any hotels that we can walk to from the Taj Mahal?':{
        'chapter': 4,
        'parsed_mrl': "query(around(center(nwr(keyval('name','Taj Mahal'))),search(nwr(keyval('tourism','hotel'))),maxdist(3000)),qtype(findkey('website')))",
        'feedback_mrl': "query(around(center(nwr(keyval('name','Taj Mahal'))),search(nwr(keyval('tourism','hotel'))),maxdist(WALKING_DIST)),qtype(least(topx(1))))",
    },
    'Name the synagogue that is closest to the Országház in Budapest!': {
        'chapter': 5,
        'parsed_mrl':  "query(around(center(area(keyval('name','Budapest')),nwr(keyval('name','Országház'))),search(nwr(keyval('amenity','place_of_worship'))),maxdist(DIST_INTOWN)),qtype(latlong))",
        'feedback_mrl':  "query(around(center(area(keyval('name','Budapest')),nwr(keyval('name','Országház'))),search(nwr(keyval('amenity','place_of_worship'),keyval('religion','jewish'))),maxdist(DIST_INTOWN),topx(1)),qtype(findkey('name')))",
    },
    'How far is it from Rotes Rathaus in Berlin to the next restaurant serving some vegetarian food?': {
        'chapter': 6,
        'parsed_mrl': "dist(query(around(center(area(keyval('name','Berlin')),nwr(keyval('name','Rotes Rathaus'))),search(nwr(keyval('amenity','regetarian'))),maxdist(DIST_INTOWN),topx(1)),qtype(latlong)))",
        'feedback_mrl': "dist(query(around(center(area(keyval('name','Berlin')),nwr(keyval('name','Rotes Rathaus'))),search(nwr(keyval('amenity','restaurant'),keyval('diet:vegetarian',or('only','yes')))),maxdist(DIST_INTOWN),topx(1)),qtype(latlong)))",
    },
    'Tell me the distance between Empire State Building in New York City and Bratislavský hrad': {
        'chapter': 7,
        'parsed_mrl': "dist(query(around(center(area(keyval('name','New York City')),nwr(keyval('name','Empire State Building'))),search(nwr(keyval('name','Bratislavský hrad'))),maxdist(DIST_INTOWN),topx(1)),qtype(latlong)))",
        'feedback_mrl': "dist(query(area(keyval('name','New York City')),nwr(keyval('name','Empire State Building')),qtype(latlong)),query(nwr(keyval('name','Bratislavský hrad')),qtype(latlong)))",
    },
}


def tutorial_dummy_parser(nl):
    instructions = NL_TO_INSTRUCTIONS.get(nl)
    if instructions:
        mrl = instructions['parsed_mrl']
        lin = linearise(mrl)
        time.sleep(2)
        return ParseResult(success=True, nl=nl, lin=lin, mrl=mrl,
                           model='tutorial')
    return None


def get_user_chapter():
    if current_user.is_authenticated:
        return current_user.tutorial_chapter
    return session.get('tutorial_chapter', 0)


def set_user_chapter(chapter_finished):
    if chapter_finished == len(CHAPTERS) - 1:
        # Tutorial is finished. Set to -1.
        chapter_to_set = -1
    else:
        chapter_to_set = chapter_finished + 1

    if current_user.is_authenticated:
        current_user.tutorial_chapter = chapter_to_set
        db.session.add(current_user)
        db.session.commit()
    else:
        session['tutorial_chapter'] = chapter_to_set


def tutorial_dummy_saver(feedback):
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
        return feedback, 400

    feedback['error'] = ('The NL {!r} does not occur in the tutorial.'
                         .format(feedback['nl']))
    return feedback, 400
