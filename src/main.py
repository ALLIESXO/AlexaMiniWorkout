# coding=utf-8
from workout_controller import WorkoutController
from flask import Flask, render_template
from flask_ask import Ask, request, context, statement, question, session, delegate
from utils.states_enum import States
from utils.session_attributes_enum import Attributes
import time


app = Flask(__name__)
ask = Ask(app, "/")

wc = WorkoutController()

"""
Launches the app and checks if the current user exists in our database.
If user exists we greet him as we would know him already. 
"""
@ask.launch
def launched():
    session.attributes[Attributes.workout.value] = None
    session.attributes[Attributes.excercise_start_time.value] = None
    session.attributes[Attributes.quickstart.value] = 0
    session.attributes[Attributes.workout_length.value] = 7
    session.attributes[Attributes.workout_body_part.value] = 0
    session.attributes[Attributes.workout_intensity.value] = 1

    if wc.check_if_user_exist(user_id=context.System.user['userId']) is True:
        print str(context.System.user['userId'])
        session.attributes[Attributes.state.value] = States.GREETING_KNOWN.value
        return question(WorkoutController.get_speech(session.attributes[Attributes.state.value]))
    else:
        session.attributes[Attributes.state.value] = States.GREETING.value
        return question(WorkoutController.get_speech(session.attributes[Attributes.state.value]))


@ask.intent("DelegateIntent")
def DelegateIntent():
    state = session.attributes[Attributes.state.value]
    spoken_text = request.intent.slots.any.value

    if state == States.GREETING.value or state == States.GREETING_KNOWN.value:
        return greeting_fcn(spoken_text)

    elif state == States.TYPE_OF_WORKOUT.value:
        return type_of_workout_fcn(spoken_text)

    elif state == States.QUESTION.value:
        return question_fcn()


def greeting_fcn(spoken_text):
    # Emotionen herausfinden und ihn nach quickstart fragen
    feeling = wc.check_context_wit_ai(spoken_text)

    if feeling == 'verygood':
        session.attributes[Attributes.workout_intensity.value] = 5

    elif feeling == 'good':
        session.attributes[Attributes.workout_intensity.value] = 4

    elif feeling == 'normal':
        session.attributes[Attributes.workout_intensity.value] = 3

    elif feeling == 'bad':
        session.attributes[Attributes.workout_intensity.value] = 2

    elif feeling == 'verybad':
        session.attributes[Attributes.workout_intensity.value] = 1

    else:
        session.attributes[Attributes.workout_intensity.value] = 3

    session.attributes[Attributes.state.value] = States.TYPE_OF_WORKOUT.value

    return question(WorkoutController.get_speech(session.attributes[Attributes.state.value]))


def type_of_workout_fcn(spoken_text):
    dialog_context = wc.check_context_wit_ai(spoken_text)

    if dialog_context == 'user_workout':
        session.attributes[Attributes.state.value] = States.CHOOSE_WORKOUT.value
        return question(WorkoutController.get_speech(session.attributes[Attributes.state.value]))
    elif dialog_context == 'alexa_workout':
        session.attributes[Attributes.state.value] = 'workout_begin'
        session.attributes[Attributes.quickstart.value] = 1

        answer = workout_begin()

        if answer[1] == 1:
            return statement(answer[0])
        else:
            return question(answer[0])

    else:
        return not_understood_question(dialog_context)


def question_fcn():
    session.attributes[Attributes.state.value] = session.attributes[Attributes.last_question.value]
    return question(WorkoutController.get_speech(session.attributes[Attributes.state.value]))


def not_understood_question(spoken_text):
    dialog_context = wc.check_context_wit_ai(spoken_text)
    print dialog_context
    print session.attributes['state']
    if dialog_context == 'question':
        return question(WorkoutController.get_speech(session.attributes['state']))
    else:
        return question(WorkoutController.get_speech('question'))


def workout_begin():
    """
    Chooses the workout based on all information given and then creates the correct string
    "Dein Workout besteht aus (yaml part1) " + "10 Uebungen" + "Am Anfang kannst du immer zu einer Uebung fragen ..."
    :return: String with correct number of workout exercises
    """
    # TODO: intensity is only mapped to have a value 1,2,3. Inside DB it should be 1,2,3,4,5
    intensity = session.attributes[Attributes.workout_intensity.value]
    duration = session.attributes[Attributes.workout_length.value]
    body_part = session.attributes[Attributes.workout_body_part.value]

    # When choosing workout by name this case happens
    if session.attributes[Attributes.workout.value] is not None:
        workout = session.attributes[Attributes.workout.value]
        speak_part1 = str(WorkoutController.get_speech('workout_begin_1'))
        speak_part2 = str(WorkoutController.get_speech('workout_begin_2'))

        speech = speak_part1 + ' ' + str(len(workout['exercises'])) + ' ' + speak_part2

        session.attributes['state'] = States.FIRST_EXCERCISE.value
        return speech, 0

    # Quickstart case
    elif session.attributes[Attributes.quickstart.value] == 1:
        workout = wc.get_workout_by_alexa(user_id=context.System.user['userId'], todays_form=intensity)

    # Normal case
    else:
        workout = wc.get_workout_by_user(
            intensity=intensity,
            duration=duration,
            body_part=body_part,
            user_id=1,  # ToDo use Amazon id
        )

    session.attributes[Attributes.workout.value] = workout

    if workout == -1 or workout is None:
        session.attributes['state'] = 'error'
        sorry = "Sorry aber ich habe keine Workouts auf Lager die gerade passen. " \
                + WorkoutController.get_speech('error')

        return sorry, 1

    else:
        speak_part1 = str(WorkoutController.get_speech('workout_begin_1'))
        speak_part2 = str(WorkoutController.get_speech('workout_begin_2'))

        speech = speak_part1 + ' ' + str(len(workout['exercises'])) + ' ' + speak_part2

        session.attributes[Attributes.state.value] = States.FIRST_EXCERCISE.value
        return speech, 0


if __name__ == '__main__':
    app.run(debug=True)
