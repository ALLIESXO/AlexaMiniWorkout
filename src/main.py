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
    session.attributes['workout_body_part'] = 0
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
            # standard param

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

        context_state = WorkoutController.check_context_wit_ai(spoken_text)

        if context_state == "lowerbody":
            session.attributes['workout_body_part'] = 3
        elif context_state == "core":
            session.attributes['workout_body_part'] = 2
        elif context_state == "upperbody":
            session.attributes['workout_body_part'] = 1
        else:
            session.attributes['workout_body_part'] = 0

        session.attributes['state'] = 'difficulty'
        return question(WorkoutController.get_speech(session.attributes['state']))

    elif state == 'difficulty':
        context_state = WorkoutController.check_context_wit_ai(spoken_text)

        if context_state == 'easy':
            session.attributes['workout_intensity'] = 1
        elif context_state == 'schwer':
            session.attributes['workout_intensity'] = 3
        else:
            session.attributes['workout_intensity'] = 2

        session.attributes['state'] = 'workout_begin'
        return question(workout_begin())

# ####### Starting Workout #########

    elif state == 'first_workout':
        workout = session.attributes['workout']
        context_state = WorkoutController.check_context_wit_ai(spoken_text)

        if context_state != 'exercise_question':
            tmp = WorkoutController.get_speech('first_workout')
            speech_1 = tmp + ' ' + str(workout['exercises'][0]['name'])
            speech_2 = WorkoutController.get_speech('countdown_start')
            speech = speech_1 + speech_2

            session.attributes['ex_count'] = 1
            session.attributes['state'] = 'next_workout'
            return question(speech)

        else:
            session.attributes['state'] = 'ex_question'
            return question(workout['exercises'][0]['description'] + ' Bist du jetzt bereit?')

    elif state == 'next_workout':

        count = session.attributes['ex_count']
        if count < len(session.attributes['workout']['exercises']):
            workout = session.attributes['workout']['exercises'][count]['name']
            speech_1 = WorkoutController.get_speech('next_workout')
            speech_2 = WorkoutController.get_speech('countdown_start')

            speech = speech_1 + ' ' + str(workout) + ' ' + speech_2
            session.attributes['ex_count'] = count + 1
            return question(speech)

        else:
            session.attributes['state'] = 'workout_done'
            speech_1 = WorkoutController.get_speech('workout_done_1')
            speech_2 = WorkoutController.get_speech('workout_done_2')
            # TODO: wieviele punkte bekommt der user ?
            speech = speech_1 + ' 5 Punkte dazubekommen. ' + speech_2
            return question(speech)

    elif state == 'workout_done':
        context = WorkoutController.check_context_wit_ai(spoken_text)

        # user will retro machen
        if context is 'yes':
            session.attributes['state'] = 'retrospective_start'
            return question(WorkoutController.get_speech('overall'))

        else:
            session.attributes['state'] = 'farewell'
            return statement(WorkoutController.get_speech('farewell'))

    # ##### Retrospective begins here  #########

    elif state == 'retrospective_start':
        # TODO: save retrospective in DB (some are just dummies)
        # TODO: analyze using intents
        session.attributes['state'] = 'specific_easy'
        return question(WorkoutController.get_speech('specific_easy'))

    elif state == 'specific_easy':
        # TODO: save retrospective in DB (some are just dummies)
        # TODO: analyze using intents
        session.attributes['state'] = 'specific_hard'
        return question(WorkoutController.get_speech('specific_hard'))

    elif state == 'specific_hard':
        # TODO: save retrospective in DB (some are just dummies)
        # TODO: analyze using intents

        # TODO: IF NO DATA OF USER EXISTS about this question
        session.attributes['state'] = 'day_time_training'
        return question(WorkoutController.get_speech('day_time_training'))

    elif state == 'day_time_training':
        # TODO: save retrospective in DB (some are just dummies)
        # TODO: analyze using intents
        session.attributes['state'] = 'farewell_retro'
        return question(WorkoutController.get_speech('farewell_retro'))

    else:
        return statement(WorkoutController.get_speech('error'))


def workout_begin():
    """
    Chooses the workout based on all information given and then creates the correct string
    "Dein Workout besteht aus (yaml part1) " + "10 Uebungen" + "Am Anfang kannst du immer zu einer Uebung fragen ..."
    :return: String with correct number of workout exercises
    """
    # TODO: intensity is only mapped to have a value 1,2,3. Inside DB it should be 1,2,3,4,5
    intensity = session.attributes['workout_intensity']
    duration = session.attributes['workout_length']
    body_part = session.attributes['workout_body_part']

    workout = wc.get_workout_by_user(
        intensity=intensity,
        duration=duration,
        body_part=body_part,
        user_id=context.System.user['userId']
    )
    session.attributes['workout'] = workout

    if workout is -1:
        session.attributes['state'] = 'error'
        return statement("Sorry aber ich habe keine Workouts auf Lager die gerade passen.")

    else:
        speak_part1 = str(WorkoutController.get_speech('workout_begin_1'))
        speak_part2 = str(WorkoutController.get_speech('workout_begin_2'))

        speech = speak_part1 + ' ' + str(len(workout['exercises'])) + ' ' + speak_part2

        session.attributes['state'] = 'first_workout'
        return speech


if __name__ == '__main__':
    app.run(debug=True)
