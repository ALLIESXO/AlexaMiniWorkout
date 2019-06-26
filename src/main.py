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
    session.attributes['workout_intensity'] = "normal"

    if wc.check_if_user_existed(user_id=context.System.user['userId']) is True:
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

    elif state == 'body_part':   # TODO: WIT AI INTENT

        lower_body = ["beine","unterschenkel","oberschenkel", "unter", "unterkoerper","unteren"]
        core = ["bauch","ruecken","brust"]
        upper_body = ["arme","schultern","bizeps","trizeps"]

        if any(word in spoken_text for word in lower_body):
            session.attributes['workout_body_part'] = 3
        elif any(word in spoken_text for word in core):
            session.attributes['workout_body_part'] = 2
        elif any(word in spoken_text for word in upper_body):
            session.attributes['workout_body_part'] = 1
        else:
            session.attributes['workout_body_part'] = 0

        session.attributes['state'] = 'difficulty'
        return question(WorkoutController.get_speech(session.attributes['state']))

    elif state == 'difficulty':

        if 'leicht' in spoken_text:
            session.attributes['workout_intensity'] = "leicht"
        elif 'schwer' in spoken_text:
            session.attributes['workout_intensity'] = "schwer"

        session.attributes['state'] = 'workout_begin'
        # return question(workout_begin())
        # TODO: Remove this statement
        return statement("Mehr kann ich grade nicht mehr fragen :D")

    else:
        return statement(WorkoutController.get_speech('error'))


def workout_begin():
    """
    Chooses the workout based on all information given and then creates the correct string
    "Dein Workout besteht aus (yaml part1)"+ "10 Uebungen" + "Am Anfang kannst du immer zu einer Uebung fragen ..."
    :return: String with correct number of workout exercises
    """

    return None


if __name__ == '__main__':
    app.run(debug=True)
