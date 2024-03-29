#!/usr/bin/python
from db_manager import DbManager
import yaml
import codecs
import json
import numpy
import pendulum
import random
from ibm_watson import LanguageTranslatorV3
from ibm_watson import ToneAnalyzerV3  # pip install --upgrade "ibm-watson>=3.0.3"
from wit import Wit  # pip install wit


class WorkoutController:

    def __init__(self):
        self.db = DbManager()

    def get_workout_by_name(self, name):
        return self.db.select_workout_by_name(name)

    def check_if_user_exist(self, user_id):
        if len(self.db.get_last_user_workouts(user_id)) > 0:
            return True
        else:
            # TODO: Save user in DB
            return False

    def save_user_workout(self, user_id, workout_id, intensity_rating, daily_form):
        self.db.save_user_workout(user_id, workout_id, intensity_rating, daily_form)

    def get_workout_by_user(self, intensity, duration, body_part, user_id):
        """
        Get a workout depending on the parameters the user told alexa
        :param intensity:
        :param duration:
        :param body_part:
        :param user_id:
        :return:
        """

        'get all workouts from db that match the selected intensity value'
        workouts = self.db.select_workouts_by_user_parameters(intensity)
        workouts_body_part_match = []
        workouts_duration_match = []

        if workouts.__len__() == 0:
            'there is no such workout'
            return []

        if workouts.__len__() > 1:
            'get the last user workout from db'
            last_user_workout = self.db.get_last_user_workout(user_id)

            index = 0
            while index < workouts.__len__():
                workout = workouts[index]
                workout_removed = False

                'exclude the last done workout from match list'
                if workout["workout"]["id"] == last_user_workout["workout_id"]:
                    workout_removed = True
                else:
                    'exclude such workouts that do not match the selected body part'
                    if workout["workout"]["body_part"] != body_part:
                        workout_removed = True
                    else:
                        workouts_body_part_match.append(workout)

                    'exclude such workouts that do not match the selected duration'
                    if workout["workout"]["duration"] != duration:
                        workout_removed = True
                    else:
                        workouts_duration_match.append(workout)

                if workout_removed:
                    workouts.remove(workout)
                    index -= 1

                index += 1

            'if the workouts list does still contain workouts then they exactly match the given parameters' \
                'select a workout at random to return'
            if workouts.__len__() > 0:
                random.shuffle(workouts)
                return workouts[0]

            'prioritize matching body parts over matching durations' \
                'select a workout at random to return'
            if workouts_body_part_match.__len__() > 0:
                random.shuffle(workouts_body_part_match)
                return workouts_body_part_match[0]

            if workouts_duration_match.__len__() > 0:
                random.shuffle(workouts_duration_match)
                return workouts_duration_match[0]

            'fall back option if no workout was found in db that matches any of the given parameters' \
                'return the last done workout again'
            return last_user_workout
        else:
            'return the only workout with this parameters'
            return workouts[0]

    def get_workout_by_alexa(self, user_id, todays_form):
        """
        IN PROGRESS
        This function is used if alexa should choose a workout.
        In this case alexa takes the previous done workouts into account
        and tries to select a good workout for the user

        Alexa takes following parameters into account:
        - The last workout intensity
        - The last workout body part
        - The last workout intensity rating
        - The last workout fitness rating
        - The overall development of the user
        :return: the workout selected
        """

        last_user_workout = self.db.get_last_user_workout(user_id)

        if last_user_workout is not None:
            """
            Calculate best workout
            """
            low_duration = 7
            high_duration = 14

            selected_duration = 7

            last_workout_data = self.db.select_workout_by_id(last_user_workout['workout_id'])['workout'][0]
            last_rated_intensity = last_user_workout['intensity_rating']
            last_workout_total_intensity = last_workout_data['intensity']
            last_workout_duration = last_workout_data['duration']

            new_workout_intensity = self.calculate_workout_intensity(user_id, last_workout_total_intensity,
                                                                     last_rated_intensity, todays_form)

            selected_intensity = new_workout_intensity

            selected_body_part = self.calculate_workout_body_part(user_id)

            # define intensity and duration by calculated intensity
            if last_workout_total_intensity < new_workout_intensity and last_workout_duration == low_duration:
                selected_intensity = last_workout_total_intensity
                selected_duration = high_duration

            if last_workout_total_intensity < new_workout_intensity and last_workout_duration == high_duration:
                selected_intensity = new_workout_intensity
                selected_duration = low_duration

            if last_workout_total_intensity > new_workout_intensity and last_workout_duration == high_duration:
                selected_intensity = last_workout_total_intensity
                selected_duration = low_duration

            if last_workout_total_intensity < new_workout_intensity and last_workout_duration == low_duration:
                selected_intensity = new_workout_intensity
                selected_duration = high_duration

            return self.get_workout_by_user(selected_intensity, selected_duration, selected_body_part, user_id)
        else:
            """
            The user has no last workouts - Therefore select a basic beginner workout
            """
            workouts = self.db.select_workout_by_intensity_and_bodypart(1, 0)

            if workouts.__len__() > 0:
                return workouts[0]
            else:
                return []

    def calculate_workout_body_part(self, user_id):
        last_user_workouts = self.db.get_last_user_workouts(user_id)

        if last_user_workouts.__len__() > 1:
            recent_workout = last_user_workouts[0]
            previous_workout = last_user_workouts[1]

            today = pendulum.now()
            week_start = today.start_of('week')

            tz = pendulum.timezone('Europe/Paris')
            previous_workout_date = pendulum.from_timestamp(previous_workout["workout_date"])
            previous_workout_date = tz.convert(previous_workout_date)

            if week_start <= previous_workout_date:
                recent_workout_body_part = self.db.select_workout_by_id(recent_workout['workout_id'])['workout'][0][
                    "body_part"]
                previous_workout_body_part = self.db.select_workout_by_id(previous_workout['workout_id'])['workout'][0][
                    "body_part"]

                body_parts_array = numpy.arange(4)

                body_parts_array = body_parts_array[body_parts_array != recent_workout_body_part]

                body_parts_array = body_parts_array[body_parts_array != previous_workout_body_part]

                if body_parts_array.__len__() == 3:
                    return random.choice(body_parts_array)

                if body_parts_array.__len__() == 2:
                    if recent_workout_body_part != 0 and previous_workout_body_part != 0:
                        return body_parts_array[body_parts_array != 0][0]
                    else:
                        return random.choice(body_parts_array)
            else:
                return 0
        else:
            return 0

    def calculate_workout_intensity(self, user_id, last_workout_total_intensity, last_workout_intensity_rating,
                                    todays_form, ):
        """
        Based on the given parameters, this function calculates the intensity of the next workout to select
        :param user_id
        :param last_workout_total_intensity:
        :param last_workout_intensity_rating:
        :param todays_form:
        :return:
        """
        fitness_median = self.calculate_fitness_median(user_id)
        last_intense_delta = last_workout_total_intensity - last_workout_intensity_rating
        form_delta = todays_form - fitness_median

        min_intensity = 1
        max_intensity = 5

        intensity_to_return = min_intensity

        if -2 < last_intense_delta < 2:
            if -2 < form_delta < 2:
                if last_intense_delta == -1:
                    if form_delta > 0:
                        intensity_to_return = last_workout_total_intensity
                    else:
                        intensity_to_return = last_workout_total_intensity - 1
                if last_intense_delta == 0:
                    intensity_to_return = last_workout_total_intensity
                if last_intense_delta == 1:
                    if form_delta < 0:
                        intensity_to_return = last_workout_total_intensity
                    else:
                        intensity_to_return = last_workout_total_intensity + 1
            if form_delta < -1:
                intensity_to_return = last_workout_total_intensity - 1
            if form_delta > 1:
                intensity_to_return = last_workout_total_intensity + 1
        else:
            if last_intense_delta < -1:
                intensity_to_return = last_workout_total_intensity - 1
            if last_intense_delta > 1:
                intensity_to_return = last_workout_total_intensity + 1

        if intensity_to_return < min_intensity:
            intensity_to_return = min_intensity

        if intensity_to_return > max_intensity:
            intensity_to_return = max_intensity

        return intensity_to_return

    def calculate_fitness_median(self, user_id):
        """
        Calculates the median of the last fitness forms of the user
        :return:
        """
        fitness_array = self.db.get_user_fitness_ratings_array(user_id)

        if fitness_array:
            return numpy.round(numpy.median(fitness_array))

        return 0

    # chooses a random sentence from bunch of templates. State maps to the templates of the yaml
    @staticmethod
    def get_speech(state):

        with codecs.open('speechCollection.yaml', 'r', encoding='utf-8') as stream:
            doc = yaml.load(stream)
            speech_list = doc[state]

            random.shuffle(speech_list)
            alexa_speaks = speech_list[0]
            try:
                alexa_speaks = alexa_speaks.encode('utf-8')
            except AttributeError:
                print alexa_speaks
                alexa_speaks = speech_list[0]

        return alexa_speaks

    @staticmethod
    def analyze_emotion_by_text(untranslated_text):
        """
        The function translates german text inside the ibm cloud and then sends them to the
        ibm cloud watson emotion analyzer - after that the result is checked
        :param untranslated_text: contains the german text recognised by alexa
        :return: Number in range 1 to 5
        """

        language_translator = LanguageTranslatorV3(
            version='2019-06-25',
            iam_apikey='XXX-XXX-XXX', # replace here api key IBM Language Translator
            url='https://gateway-fra.watsonplatform.net/language-translator/api'
        )
        translated_text = language_translator.translate(text=untranslated_text, model_id='de-en').get_result()
        print(json.dumps(translated_text, indent=2, ensure_ascii=False)).encode('utf8')

        tone_analyzer = ToneAnalyzerV3(
            version='2019-06-25',
            iam_apikey='XXX-XXX-XXX', # replace here api key IBM Watson Tone Analyzer
            url='https://gateway-fra.watsonplatform.net/tone-analyzer/api',
        )

        translated_text = yaml.load(json.dumps(translated_text))  # decodes unicode dictionary. only cuz python2.7
        translated_text = translated_text['translations'][0]['translation']

        tone_analysis = tone_analyzer.tone(
            {'text': translated_text},
            content_type='application/json'
        ).get_result()
        print(json.dumps(tone_analysis, indent=2)).encode('utf8')

        return WorkoutController._get_emotion_level_based_on_json(tone_analysis)

    @staticmethod
    def _get_emotion_level_based_on_json(tone_analysis):
        """
        Chooses the level of confidence (1-5) for the workout based on the emotions.
        :param tone_analysis: analysis of the emotion as json (dict)
        :return:
        """

        # if the analyzer could not figure it out map to normal mood
        emotion_dict = tone_analysis["document_tone"]["tones"]
        if len(emotion_dict) < 1:
            return 3
        # when there is only one emotion recognized
        elif len(emotion_dict) < 2:
            if emotion_dict[0]['tone_name'] == 'Joy':
                return 5

            elif emotion_dict[0]['tone_name'] == 'Anger':
                return 4

            elif emotion_dict[0]['tone_name'] == 'Confident':
                if emotion_dict[0]['score'] > 0.9:
                    return 4
                else:
                    return 3

            elif emotion_dict[0]['tone_name'] == 'Sadness':
                return 1

            elif emotion_dict[0]['tone_name'] == 'Tentative':
                return 3

            elif emotion_dict[0]['tone_name'] == 'Analytical':
                return 2

            else:
                return 3

        # there are more than two emotion recognised
        else:
            # find the two most highest emotions
            list_of_emotions = []
            for emotion in emotion_dict:
                list_of_emotions.append((emotion['tone_name'], emotion['score']))
            list_of_emotions.sort(key=lambda x: x[1], reverse=True)
            print(list_of_emotions)

            if list_of_emotions[0][0] == 'Joy':
                return 5

            elif list_of_emotions[0][0] == 'Anger':
                return 4

            elif list_of_emotions[0][0] == 'Confident':

                if list_of_emotions[1][0] == 'Anger':
                    return 4
                elif list_of_emotions[1][0] == 'Sadness':
                    return 1
                elif list_of_emotions[1][0] == 'Analytical':
                    return 4
                elif list_of_emotions[1][0] == 'Joy':
                    return 4
                elif list_of_emotions[1][0] == 'Fear':
                    return 2
                elif list_of_emotions[1][0] == 'Tentative':
                    return 3
                else:
                    return 3

            elif list_of_emotions[0][0] == 'Sadness':

                if list_of_emotions[1][0] == 'Joy':
                    return 2
                elif list_of_emotions[1][0] == 'Anger':
                    return 3
                elif list_of_emotions[1][0] == 'Confident':
                    return 2
                else:
                    return 1

            elif list_of_emotions[0][0] == 'Tentative':
                if list_of_emotions[1][0] == 'Joy':
                    return 4
                elif list_of_emotions[1][0] == 'Analytical':
                    return 3
                elif list_of_emotions[1][0] == 'Sadness':
                    return 2
                elif list_of_emotions[1][0] == 'Fear':
                    return 2
                else:
                    return 3

            elif list_of_emotions[0][0] == 'Analytical':
                if list_of_emotions[1][0] == 'Joy':
                    return 4
                elif list_of_emotions[1][0] == 'Sadness':
                    return 2
                elif list_of_emotions[1][0] == 'Fear':
                    return 2
                elif list_of_emotions[1][0] == 'Confident':
                    return 4
                else:
                    return 3

            else:
                return 3

    @staticmethod
    def check_context_in_text(spoken_text, list1, list2):
        """
        This is a fallback method if something wents wrong with wit.ai
        Checks the context of the user, given to lists with possible answers which could be inside.
        E.g. Alexa: "Which exercise do you want? A premade or a specifc?
             User : "I would like to have ... uhm.. a specific one?
             First list would be ["yours","alexa","premade"]
             Second list would be ["mine","specific","not premade"]
             The list with the most occurrences will be the context.
        :param spoken_text: spoken words by user
        :param list1: possible words which should occur in list
        :param list2: possible words which should occur in list
        :return: The list with the most occurrences (context).
        """

        context1 = 0
        context2 = 0

        if any(word in spoken_text for word in list1):
            context1 = + 1

        if any(word in spoken_text for word in list2):
            context2 = + 2

        print(context1)

        if context1 > context2:
            return list1
        elif context2 > context1:
            return list2
        else:
            return []

    @staticmethod
    def check_context_wit_ai(spoken_text):
        """
        Sends the spoken text to wit.ai and recognizes the context/intent of it and passes a json back.
        :param spoken_text: german spoken text by the user
        :return: context as string
        """

        client = Wit('XXX') # replace here API key wit ai
        response = client.message(spoken_text)
        # return found intent
        print response
        try:
            answer = response['entities'].keys()[0]
        except IndexError:
            return "not_found"

        return answer

    @staticmethod
    def get_feedback_out_of_context(spoken_text):

        emotion = WorkoutController.analyze_emotion_by_text(spoken_text)
        feeling = WorkoutController.check_context_wit_ai(spoken_text)

        result_of_feeling = emotion

        if result_of_feeling > 5:
            result_of_feeling = 5
        elif result_of_feeling < 1:
            result_of_feeling = 1

        result_of_feeling = int(round(result_of_feeling))

        return result_of_feeling

