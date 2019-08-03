from enum import Enum


class States(Enum):
    GREETING = "GREETING"
    GREETING_KNOWN = "GREETING_KNOWN"

    TYPE_OF_WORKOUT = "TYPE_OF_WORKOUT"
    CHOOSE_WORKOUT = "CHOOSE_WORKOUT"
    WORKOUT_BEGIN = "WORKOUT_BEGIN"

    LENGTH_OF_WORKOUT = "LENGTH_OF_WORKOUT"
    BODYPART = "BODYPART"
    TRAIN_SPECIFIC = "TRAIN_SPECIFIC"
    DIFFICULTY = "DIFFICULTY"

    QUESTION = "QUESTION"

    COUNTDOWN_START = "COUNTDOWN_START"
    COUNTDOWN_START_2 = "COUNTDOWN_START_2"
    COUNTDOWN_START_LAST_EXERCISE = "COUNTDOWN_START_LAST_EXERCISE"
    FIRST_EXCERCISE = "FIRST_EXCERCISE"
    NEXT_EXCERCISE = "NEXT_EXCERCISE"
    IN_EXCERCISE = "IN_EXCERCISE"
    EXERCISE_PAUSE = "EXERCISE_PAUSE"
    EXERCISE_QUESTION = "EXERCISE_QUESTION"
    KEEP_GOING_2 = "KEEP_GOING_2"
    KEEP_GOING_1 = "KEEP_GOING_1"
    UNINTENDED_PAUSE = "UNINTENDED_PAUSE"
    PAUSE = "PAUSE"
    PAUSE_ERROR = "PAUSE_ERROR"

    WORKOUT_DONE = "WORKOUT_DONE"

    RETROSPECTIVE_START = "RETROSPECTIVE_START"
    ASK_RETROSPECTIVE = "ASK_RETROSPECTIVE"
    SPECIFIC_EASY = "SPECIFIC_EASY"
    SPECIFIC_HARD = "SPECIFIC_HARD"
    DAY_TIME_TRAINING = "DAY_TIME_TRAINING"
    FAREWELL_RETRO = "FAREWELL_RETRO"

    FAREWELL = "FAREWELL"
