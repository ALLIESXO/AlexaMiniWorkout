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
    if wc.check_if_user_existed(user_id=context.System.user['userId']) is True:
        print str(context.System.user['userId'])
        session.attributes['state'] = 'greeting_known'
        return question(WorkoutController.get_speech(session.attributes['state']))
    else:
        session.attributes['state'] = 'greeting'
        return question(WorkoutController.get_speech(session.attributes['state']))


@ask.intent("RatingIntent")
def RatingIntent():
    session.attributes['state'] = 'choose_workout'
    WorkoutController.get_emotions_of_text(request.intent.slots.any.value)
    return question(WorkoutController.get_speech(session.attributes['state']))


if __name__ == '__main__':
    app.run(debug=True)
