from workout_controller import WorkoutController
from flask import Flask, render_template
from flask_ask import Ask, request, context, statement, question, session, delegate
import yaml
import codecs
import random

app = Flask(__name__)
ask = Ask(app, "/")


@ask.launch
def launched():
    session.attributes['state'] = 'greeting'
    return question(get_speech(session.attributes['state']))


def get_speech(state):

    with codecs.open('speechCollection.yaml', 'r', encoding='utf-8') as stream:
        doc = yaml.load(stream)
        speech_list = doc[state]
        random.shuffle(speech_list)
        alexa_speaks = speech_list[0]

    return alexa_speaks


if __name__ == '__main__':
    app.run(debug=True)
