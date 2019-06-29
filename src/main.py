# coding=utf-8
from workout_controller import WorkoutController
from flask import Flask, render_template
from flask_ask import Ask, request, context, statement, question, session, delegate



app = Flask(__name__)
ask = Ask(app, "/")

wc = WorkoutController()

"""
Launches the app and checks if the current user exists in our database.
If user exists we greet him as we would know him already. 
"""
@ask.launch
def launched():
    session.attributes['quickstart'] = 0
    session.attributes['workout_length'] = 7
    session.attributes['workout_body_part'] = ""
    session.attributes['workout_intensity'] = 2 # TODO: What is the standard value ?

    if wc.check_if_user_exist(user_id=context.System.user['userId']) is True:
        print str(context.System.user['userId'])
        session.attributes['state'] = 'greeting_known'
        return question(WorkoutController.get_speech(session.attributes['state']))
    else:
        session.attributes['state'] = 'greeting'
        return question(WorkoutController.get_speech(session.attributes['state']))


@ask.intent("DelegateIntent")
def DelegateIntent():
    state = session.attributes['state']
    spoken_text = request.intent.slots.any.value

    # Emotionen herausfinden und ihn nach quickstart fragen
    if state == 'greeting' or state == 'greeting_known':
        WorkoutController.analyze_emotion_by_text(spoken_text)
        session.attributes['state'] = 'choose_workout'
        return question(WorkoutController.get_speech(session.attributes['state']))

    # Moechte er Quickstart oder normal Workout auswaehlen
    elif state == 'choose_workout':
        dialog_context = WorkoutController.check_context_wit_ai(spoken_text)
        if dialog_context == 'yes':
            session.attributes['state'] = 'type_of_workout'
            return question(WorkoutController.get_speech(session.attributes['state']))
        else:
            session.attributes['state'] = 'length_of_workout'
            session.attributes['quickstart'] = 1
            return question(WorkoutController.get_speech(session.attributes['state']))

    # Quickstart -> Frage nach ob er ein 7 oder 14 minuten Workout machen moechte.
    elif state == 'length_of_workout' and session.attributes['quickstart'] == 1:
        dialog_context = WorkoutController.check_context_wit_ai(spoken_text)
        if dialog_context == 'long_workout':
            session.attributes['workout_length'] = 14
        else:
            session.attributes['workout_length'] = 7

        session.attributes['state'] = 'workout_begin'
        return question(workout_begin())

    # Normal Workout auswaehlen (kein Quickstart) - Alexa oder Benutzer Workout ?
    elif state == 'type_of_workout':
        dialog_context = WorkoutController.check_context_wit_ai(spoken_text)
        if dialog_context == 'user_workout':
            session.attributes['state'] = 'type_user_workout'
            return question(WorkoutController.get_speech(session.attributes['state']))
        else:
            session.attributes['state'] = 'length_of_workout'
            return question(WorkoutController.get_speech(session.attributes['state']))

    elif state == 'length_of_workout' and session.attributes['quickstart'] == 0:
        dialog_context = WorkoutController.check_context_wit_ai(spoken_text)

        if dialog_context == 'long_workout':
            session.attributes['workout_length'] = 14
        else:
            session.attributes['workout_length'] = 7
        session.attributes['state'] = 'shall_we_train_specific'
        return question(WorkoutController.get_speech(session.attributes['state']))

    elif state == 'shall_we_train_specific':
        dialog_context = WorkoutController.check_context_wit_ai(spoken_text)

        if dialog_context == "yes":
            session.attributes['state'] = 'body_part'
            return question(WorkoutController.get_speech(session.attributes['state']))
        else:
            session.attributes['state'] = 'difficulty'
            return question(WorkoutController.get_speech(session.attributes['state']))

    elif state == 'body_part':

        context = WorkoutController.check_context_wit_ai(spoken_text)

        if context == "lowerbody":
            session.attributes['workout_body_part'] = 3
        elif context == "core":
            session.attributes['workout_body_part'] = 2
        elif context == "upperbody":
            session.attributes['workout_body_part'] = 1
        else:
            session.attributes['workout_body_part'] = 0

        session.attributes['state'] = 'difficulty'
        return question(WorkoutController.get_speech(session.attributes['state']))

    elif state == 'difficulty':

        if 'leicht' in spoken_text:
            session.attributes['workout_intensity'] = 1
        elif 'schwer' in spoken_text:
            session.attributes['workout_intensity'] = 3

        session.attributes['state'] = 'workout_begin'
        return question(workout_begin())

# ####### Starting Workout #########

    elif state == 'first_workout':
        session.attributes['workout']


    else:
        return statement(WorkoutController.get_speech('error'))


def workout_begin():
    """
    Chooses the workout based on all information given and then creates the correct string
    "Dein Workout besteht aus (yaml part1) " + "10 Uebungen" + "Am Anfang kannst du immer zu einer Uebung fragen ..."
    :return: String with correct number of workout exercises
    """
    # TODO: intensity is only mapped to have a value 1,2,3. Inside DB it should be 1,2,3,4,5
    intensity = session.attributes['workout_body_part']
    duration = session.attributes['workout_length']
    body_part = session.attributes['workout_body_part']

    workout = wc.get_workout_by_user(
        intensity=intensity,
        duration=duration,
        body_part=body_part,
        user_id=context.System.user['userId']
    )
    session.attributes['workout'] = workout

    if workout is []:
        session.attributes['state'] = 'error'
        return statement("Sorry aber ich habe keine Workouts auf Lager die gerade passen.")

    else:
        speech = WorkoutController.get_speech('workout_begin_1') \
                 + ' ' + str(len(workout['exercises'])) + ' ' \
                 + WorkoutController.get_speech('workout_begin_2')
        session.attributes['state'] = 'first_workout'
        return question(speech)


if __name__ == '__main__':
    app.run(debug=True)
