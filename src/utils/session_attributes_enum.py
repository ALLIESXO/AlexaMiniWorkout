from enum import Enum


class Attributes(Enum):
    workout = "workout"
    workout_length = "workout_length "
    workout_body_part = "workout_body_part"
    workout_intensity = "workout_intensity"
    workout_day_form = "workout_day_form"
    workout_intensity_rating = "workout_intensity_rating"
    workout_active_time = "workout_active_time"
    workout_break_time = "workout_break_time"

    current_excercise = "current_excercise"
    excercise_start_time = "excercise_start_time"
    ex_count = "ex_count"

    quickstart = "quickstart"

    state = "state"

    last_question = "last_question"

    user_id = "user_id"
