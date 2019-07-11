# coding=utf-8
from workout_controller import WorkoutController
from flask import Flask, render_template
from flask_ask import Ask, request, context, statement, question, session, delegate
from utils.states_enum import States
from utils.session_attributes_enum import Attributes
import time
from datetime import datetime


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
    session.attributes[Attributes.workout_intensity_rating.value] = 1
    session.attributes[Attributes.workout_day_form.value] = 1

    if wc.check_if_user_exist(user_id=context.System.user['userId']) is True:
        print str(context.System.user['userId'])
        session.attributes[Attributes.state.value] = States.GREETING_KNOWN.value
        session.attributes[Attributes.user_id.value] = 1
        return question(WorkoutController.get_speech(session.attributes[Attributes.state.value]))
    else:
        session.attributes[Attributes.state.value] = States.GREETING.value
        session.attributes[Attributes.user_id.value] = 1
        return question(WorkoutController.get_speech(session.attributes[Attributes.state.value]))


@ask.intent("DelegateIntent")
def DelegateIntent():
    state = session.attributes[Attributes.state.value]
    spoken_text = request.intent.slots.any.value

    if state == States.GREETING.value or state == States.GREETING_KNOWN.value:
        return greeting_fcn(spoken_text)

    elif state == States.TYPE_OF_WORKOUT.value:
        return type_of_workout_fcn(spoken_text)

    elif state == States.LENGTH_OF_WORKOUT.value:
        return question_duration(spoken_text)

    elif state == States.TRAIN_SPECIFIC.value:
        return question_train_specific(spoken_text)

    elif state == States.BODYPART.value:
        return question_bodypart(spoken_text)

    elif state == States.DIFFICULTY.value:
        return question_difficulty(spoken_text)

    elif state == States.FIRST_EXCERCISE.value:
        return question_first_exercise(spoken_text)

    elif state == States.IN_EXCERCISE.value:
        return question_next_exercise(spoken_text, 0)

    elif state == States.WORKOUT_DONE.value:
        return question_workout_done(spoken_text)

    elif state == States.RETROSPECTIVE_START.value:
        return question_retrospective_start(spoken_text)

    elif state == States.SPECIFIC_EASY.value:
        return question_specific_easy(spoken_text)

    elif state == States.SPECIFIC_HARD.value:
        return question_specific_hard(spoken_text)

    elif state == States.DAY_TIME_TRAINING.value:
        return question_day_time_training(spoken_text)

    elif state == States.PAUSE.value:
        return question_pause(spoken_text)

    elif state == States.EXERCISE_QUESTION.value:
        session.attributes[Attributes.state.value] = States.IN_EXCERCISE.value
        return question_next_exercise(spoken_text, 1)

    elif state == States.ASK_RETROSPECTIVE.value:
        return question_ask_retrospective(spoken_text)


def greeting_fcn(spoken_text):
    # Emotionen herausfinden und ihn nach quickstart fragen
    feeling = wc.check_context_wit_ai(spoken_text)

    if feeling == 'verygood':
        session.attributes[Attributes.workout_day_form.value] = 5

    elif feeling == 'good':
        session.attributes[Attributes.workout_day_form.value] = 4

    elif feeling == 'normal':
        session.attributes[Attributes.workout_day_form.value] = 3

    elif feeling == 'bad':
        session.attributes[Attributes.workout_day_form.value] = 2

    elif feeling == 'verybad':
        session.attributes[Attributes.workout_day_form.value] = 1

    else:
        session.attributes[Attributes.workout_day_form.value] = 3

    session.attributes[Attributes.state.value] = States.TYPE_OF_WORKOUT.value

    return question(WorkoutController.get_speech(session.attributes[Attributes.state.value]))


def type_of_workout_fcn(spoken_text):
    dialog_context = wc.check_context_wit_ai(spoken_text)

    # session.attributes[Attributes.workout.value] = wc.get_workout_by_name("Test Workout")
    # session.attributes[Attributes.state.value] = 'workout_begin'
    # session.attributes[Attributes.quickstart.value] = 1
    # answer = workout_begin()
    # if answer[1] == 1:
    #     return statement(answer[0])
    # else:
    #     return question(answer[0])

    if dialog_context == 'user_workout':
        session.attributes[Attributes.state.value] = States.LENGTH_OF_WORKOUT.value
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


def question_duration(spoken_text):
    context_state = WorkoutController.check_context_wit_ai(spoken_text)

    if context_state == 'long_workout':
        session.attributes['workout_length'] = 14

    elif context_state == 'short_workout':
        session.attributes['workout_length'] = 7

    else:
        return not_understood_question(context_state)

    session.attributes[Attributes.state.value] = States.TRAIN_SPECIFIC.value
    return question(WorkoutController.get_speech(session.attributes[Attributes.state.value]))


def question_train_specific(spoken_text):
    context_state = wc.check_context_wit_ai(spoken_text)

    if context_state == "yes":
        session.attributes[Attributes.state.value] = States.BODYPART.value
        return question(WorkoutController.get_speech(session.attributes[Attributes.state.value]))
    elif context_state == "no":
        session.attributes[Attributes.state.value] = States.DIFFICULTY.value
        return question(WorkoutController.get_speech(session.attributes[Attributes.state.value]))
    else:
        return not_understood_question(context_state)


def question_bodypart(spoken_text):
    context_state = wc.check_context_wit_ai(spoken_text)

    if context_state == "lowerbody":
        session.attributes['workout_body_part'] = 3
    elif context_state == "core":
        session.attributes['workout_body_part'] = 2
    elif context_state == "upperbody":
        session.attributes['workout_body_part'] = 1
    elif context_state == "full_body":
        session.attributes['workout_body_part'] = 0

    else:
        return not_understood_question(context_state)

    session.attributes[Attributes.state.value] = States.DIFFICULTY.value
    return question(WorkoutController.get_speech(session.attributes[Attributes.state.value]))


def question_difficulty(spoken_text):
    context_state = wc.check_context_wit_ai(spoken_text)

    if context_state == 'easy':
        session.attributes[Attributes.workout_intensity.value] = 1
    elif context_state == 'schwer':
        session.attributes[Attributes.workout_intensity.value] = 3
    elif context_state == 'normal':
        session.attributes[Attributes.workout_intensity.value] = 2
    else:
        return not_understood_question(context_state)

    session.attributes[Attributes.state.value] = States.WORKOUT_BEGIN.value

    answer = workout_begin()

    if answer[1] == 1:
        return statement(answer[0])
    else:
        return question(answer[0])


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
    day_form = session.attributes[Attributes.workout_day_form.value]
    duration = session.attributes[Attributes.workout_length.value]
    body_part = session.attributes[Attributes.workout_body_part.value]

    # When choosing workout by name this case happens
    if session.attributes[Attributes.workout.value] is not None:
        workout = session.attributes[Attributes.workout.value]

        speak_part1 = str(WorkoutController.get_speech('WORKOUT_BEGIN_1'))
        speak_part2 = str(WorkoutController.get_speech('WORKOUT_BEGIN_2'))

        speech = speak_part1 + ' ' + str(len(workout['exercises'])) + ' ' + speak_part2

        session.attributes['state'] = States.FIRST_EXCERCISE.value
        session.attributes[Attributes.workout.value] = workout
        session.attributes[Attributes.workout_active_time.value] = workout['workout']['active_time']
        session.attributes[Attributes.workout_break_time.value] = workout['workout']['break_time']
        return speech, 0

    # Quickstart case
    elif session.attributes[Attributes.quickstart.value] == 1:
        workout = wc.get_workout_by_alexa(user_id=context.System.user['userId'], todays_form=day_form)

    # Normal case
    else:
        workout = wc.get_workout_by_user(
            intensity=intensity,
            duration=duration,
            body_part=body_part,
            user_id=1,  # ToDo use Amazon id
        )

    session.attributes[Attributes.workout.value] = workout
    session.attributes[Attributes.workout_active_time.value] = workout['workout']['active_time']
    session.attributes[Attributes.workout_break_time.value] = workout['workout']['break_time']

    if workout == -1 or workout is None:
        session.attributes['state'] = 'error'
        sorry = "Sorry aber ich habe keine Workouts auf Lager die gerade passen. " \
                + WorkoutController.get_speech('error')

        return sorry, 1

    else:
        speak_part1 = str(WorkoutController.get_speech('WORKOUT_BEGIN_1'))
        speak_part2 = str(WorkoutController.get_speech('WORKOUT_BEGIN_2'))

        speech = speak_part1 + ' ' + str(len(workout['exercises'])) + ' ' + speak_part2

        session.attributes[Attributes.state.value] = States.FIRST_EXCERCISE.value
        return speech, 0


def question_first_exercise(spoken_text):
    workout = session.attributes[Attributes.workout.value]
    context_state = WorkoutController.check_context_wit_ai(spoken_text)

    if context_state != 'exercise_question':
        tmp = WorkoutController.get_speech(States.FIRST_EXCERCISE.value)
        speech_1 = tmp + ' ' + str(workout['exercises'][0]['name'])
        speech_2 = WorkoutController.get_speech(States.COUNTDOWN_START.value)
        speech_3 = WorkoutController.get_speech(States.COUNTDOWN_START_2.value)
        next_exercise = str(workout['exercises'][1]['name'])
        speech = speech_1 + speech_2 + ' ' + next_exercise + ' ' + speech_3

        session.attributes[Attributes.ex_count.value] = 1
        session.attributes[Attributes.excercise_start_time.value] = time.time()
        session.attributes[Attributes.state.value] = States.IN_EXCERCISE.value

        return question(speech)
    else:
        session.attributes[Attributes.state.value] = States.EXERCISE_QUESTION.value
        return question(workout['exercises'][0]['description'] + ' Bist du jetzt bereit?')


def question_next_exercise(spoken_text, onward):
    exercise_start = session.attributes[Attributes.excercise_start_time.value]
    workout = session.attributes[Attributes.workout.value]
    active_time = session.attributes[Attributes.workout_active_time.value]
    break_time = session.attributes[Attributes.workout_break_time.value]
    count = session.attributes[Attributes.ex_count.value]

    context_state = WorkoutController.check_context_wit_ai(spoken_text)

    # Check if we re still in the exercise
    time_dif = time.time() - exercise_start

    if time_dif < active_time and context_state == 'exercise_question':
        session.attributes[Attributes.state.value] = States.EXERCISE_QUESTION.value
        session.attributes[Attributes.ex_count.value] = count - 1
        return question(workout['exercises'][count-1]['description'] + ' Kann es weiter gehen?')

    if active_time < time_dif and context_state == 'exercise_question':
        session.attributes[Attributes.state.value] = States.EXERCISE_QUESTION.value
        return question(workout['exercises'][count]['description'] + ' Kann es weiter gehen?')

    if onward == 0 and time_dif < (active_time + break_time):
        # We are still in the workout and we decide to pause the workout or go to the next excercise

        if context_state == 'pause':
            session.attributes[Attributes.state.value] = States.PAUSE.value
            session.attributes[Attributes.current_excercise.value] = count-1
            return question(WorkoutController.get_speech(States.PAUSE.value))

        elif context_state == 'next_exercise':
            session.attributes[Attributes.ex_count.value] = count
            return question_next_exercise(spoken_text, 1)

        else:
            session.attributes[Attributes.state.value] = States.PAUSE.value
            session.attributes[Attributes.current_excercise.value] = count - 1
            speech_1 = WorkoutController.get_speech(States.UNINTENDED_PAUSE.value)
            return question(speech_1)

    if count == len(session.attributes[Attributes.workout.value]['exercises']) - 1:
        workout = session.attributes[Attributes.workout.value]['exercises'][count]['name']
        speech_1 = WorkoutController.get_speech(States.NEXT_EXCERCISE.value)
        speech_2 = WorkoutController.get_speech(States.COUNTDOWN_START_LAST_EXERCISE.value)

        speech = speech_1 + ' ' + str(workout) + ' ' + speech_2
        session.attributes[Attributes.ex_count.value] = count + 1
        session.attributes[Attributes.excercise_start_time.value] = time.time()
        return question(speech)

    elif count < len(session.attributes[Attributes.workout.value]['exercises']) - 1:
        exercise = session.attributes[Attributes.workout.value]['exercises'][count]['name']
        next_exercise = str(session.attributes[Attributes.workout.value]['exercises'][count+1]['name'])
        speech_1 = WorkoutController.get_speech(States.NEXT_EXCERCISE.value)
        speech_2 = WorkoutController.get_speech(States.COUNTDOWN_START.value)
        speech_3 = WorkoutController.get_speech(States.COUNTDOWN_START_2.value)
        speech = speech_1 + ' ' + str(exercise) + ' ' + speech_2 + ' ' + next_exercise + ' ' + speech_3
        session.attributes[Attributes.ex_count.value] = count + 1
        session.attributes[Attributes.excercise_start_time.value] = time.time()

        return question(speech)

    else:
        session.attributes[Attributes.state.value] = States.WORKOUT_DONE.value
        speech_1 = WorkoutController.get_speech('WORKOUT_DONE_1')
        speech_2 = WorkoutController.get_speech('WORKOUT_DONE_2')
        # TODO: wieviele punkte bekommt der user ?
        speech = speech_1 + ' 5 Punkte dazubekommen. ' + speech_2
        return question(speech)


def question_pause(spoken_text):
    context_state = WorkoutController.check_context_wit_ai(spoken_text)

    if context_state == 'onward':
        session.attributes[Attributes.state.value] = States.IN_EXCERCISE.value
        session.attributes[Attributes.ex_count.value] = session.attributes[Attributes.current_excercise.value]
        return question_next_exercise(spoken_text, 1)

    else:
        session.attributes[Attributes.ex_count.value] = session.attributes[Attributes.current_excercise.value]
        question(WorkoutController.get_speech(States.PAUSE_ERROR.value))


def question_workout_done(spoken_text):
    feeling = WorkoutController.check_context_wit_ai(spoken_text)

    if feeling == 'difficulty_veryhard':
        session.attributes[Attributes.workout_intensity_rating.value] = 5

    elif feeling == 'difficulty_good':
        session.attributes[Attributes.workout_intensity_rating.value] = 4

    elif feeling == 'difficulty_normal':
        session.attributes[Attributes.workout_intensity_rating.value] = 3

    elif feeling == 'difficulty_easy':
        session.attributes[Attributes.workout_intensity_rating.value] = 2

    elif feeling == 'difficulty_veryeasy':
        session.attributes[Attributes.workout_intensity_rating.value] = 1

    else:
        session.attributes[Attributes.workout_intensity_rating.value] = 3

    session.attributes[Attributes.state.value] = States.ASK_RETROSPECTIVE.value
    return question(WorkoutController.get_speech(States.ASK_RETROSPECTIVE.value))


def question_ask_retrospective(spoken_text):
    context_state = WorkoutController.check_context_wit_ai(spoken_text)
    # user will retro machen
    if context_state == 'yes':
        session.attributes[Attributes.state.value] = States.RETROSPECTIVE_START.value
        return question(WorkoutController.get_speech(States.RETROSPECTIVE_START.value))

    else:
        session.attributes[Attributes.state.value] = States.FAREWELL.value
        wc.save_user_workout(session.attributes[Attributes.user_id.value],
                             session.attributes[Attributes.workout.value]["workout"]["id"],
                             session.attributes[Attributes.workout_intensity_rating.value],
                             session.attributes[Attributes.workout_day_form.value])
        return statement(WorkoutController.get_speech(States.FAREWELL.value))


def question_retrospective_start(spoken_text):
    context = WorkoutController.check_context_wit_ai(spoken_text)

    feedback = WorkoutController.get_feedback_out_of_context(spoken_text)
    # TODO: save retrospective in DB (some are just dummies)
    session.attributes[Attributes.state.value] = States.SPECIFIC_EASY.value
    return question(WorkoutController.get_speech(States.SPECIFIC_EASY.value))


def question_specific_easy(spoken_text):
    # TODO: save retrospective in DB (some are just dummies)
    feedback = WorkoutController.get_feedback_out_of_context(spoken_text)
    session.attributes[Attributes.state.value] = States.SPECIFIC_HARD.value
    return question(WorkoutController.get_speech(States.SPECIFIC_HARD.value))


def question_specific_hard(spoken_text):
    # TODO: save retrospective in DB (some are just dummies)
    feedback = WorkoutController.get_feedback_out_of_context(spoken_text)

    # TODO: IF NO DATA OF USER EXISTS about this question
    session.attributes[Attributes.state.value] = States.DAY_TIME_TRAINING.value
    return question(WorkoutController.get_speech(States.DAY_TIME_TRAINING.value))


def question_day_time_training(spoken_text):
    # TODO: save retrospective in DB (some are just dummies)
    daytime = WorkoutController.check_context_wit_ai(spoken_text)

    if daytime == 'evening':
        # TODO: save in DB
        pass

    elif daytime == 'morning':
        # TODO: save in DB
        pass

    session.attributes[Attributes.state.value] = States.FAREWELL_RETRO.value
    wc.save_user_workout(session.attributes[Attributes.user_id.value],
                         session.attributes[Attributes.workout.value]["workout"]["id"],
                         session.attributes[Attributes.workout_intensity_rating.value],
                         session.attributes[Attributes.workout_day_form.value])
    return question(WorkoutController.get_speech(States.FAREWELL_RETRO.value))


if __name__ == '__main__':
    app.run(debug=True)
