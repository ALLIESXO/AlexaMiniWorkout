#!/usr/bin/python
from db_manager import DbManager
import random
import yaml
import codecs
import json
from ibm_watson import LanguageTranslatorV3
from ibm_watson import ToneAnalyzerV3  # pip install --upgrade "ibm-watson>=3.0.3"


class WorkoutController:

    def __init__(self):
        self.db = DbManager()

    def get_workout_by_name(self, name):
        return self.db.select_workout_by_name(name)

    def check_if_user_existed(self, user_id):
        if len(self.db.get_last_user_workouts(user_id)) > 0:
            return True
        else:
            return False

    def get_workout_by_user(self, intensity, duration, body_part, user_id):
        """
        Get a workout depending on the parameters the user told alexa
        :param intensity:
        :param duration:
        :param body_part:
        :param user_id:
        :return:
        """
        workouts = self.db.select_workouts_by_user_parameters(intensity, duration, body_part)

        if workouts.__len__() == 0:
            'There is no such workout'
            return -1

        if workouts.__len__() > 1:
            'Select a workout at random taking the last done workout into account'
            last_user_workout = self.db.get_last_user_workout(user_id)

            if last_user_workout != -1:

                for workout in workouts:
                    if workout[0] == last_user_workout[0]:
                        workouts.remove(workout)
                        break

            random.shuffle(workouts)
            return workouts[0]
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
        last_workouts = self.db.get_last_user_workouts(user_id)

        if last_workouts.__len__() > 0:
            """
            Calculate best workout
            """
            last_user_workout = last_workouts[0]
            last_workout = self.db.select_workout_by_id(last_user_workout['workout_id'])['workout'][0]
            last_intensity = last_user_workout['intensity_rating']
            last_fitness_rating = last_user_workout['daily_form']

            new_workout_intensity = self.calculate_workout_intensity(last_workout['intensity'], last_intensity, todays_form, last_fitness_rating)

            return new_workout_intensity

        else:
            """
            The user has no last workouts - Therefore select a basic beginner workout
            """
            workouts = self.db.select_workout_by_intensity_and_bodypart(1, 0)

            if workouts.__len__() > 0:
                return workouts[0]
            else:
                return []

    def calculate_workout_intensity(self, last_workout_intensity, last_workout_intensity_rating, todays_form,
                                    last_workout_form):
        """
        Based on the given parameters, this function calculates the intensity of the next workout to select
        :param last_workout_intensity:
        :param last_workout_intensity_rating:
        :param todays_form:
        :param last_workout_form:
        :return:
        """

        intensity_result = last_workout_intensity - last_workout_intensity_rating
        form_result = todays_form - last_workout_form

        calculated_intensity = 3 + intensity_result + form_result

        if calculated_intensity < 1:
            calculated_intensity = 1
        if calculated_intensity > 5:
            calculated_intensity = 5

        return calculated_intensity

    # chooses a random sentence from bunch of templates. State maps to the templates of the yaml
    @staticmethod
    def get_speech(state):

        with codecs.open('speechCollection.yaml', 'r', encoding='utf-8') as stream:
            doc = yaml.load(stream)
            speech_list = doc[state]
            random.shuffle(speech_list)
            alexa_speaks = speech_list[0]

        return alexa_speaks

    @staticmethod
    def get_emotions_of_text(untranslated_text):

        language_translator = LanguageTranslatorV3(
            version='2019-06-25',
            iam_apikey='CK7wZg3en6KA8DbeS0gNWbougz9qHq9VeTfXn105nuK-',
            url='https://gateway-fra.watsonplatform.net/language-translator/api'
        )
        translated_text = language_translator.translate(text=untranslated_text, model_id='de-en').get_result()
        print(json.dumps(translated_text, indent=2, ensure_ascii=False)).encode('utf8')

        tone_analyzer = ToneAnalyzerV3(
            version='2019-06-25',
            iam_apikey='oWwv8FrexMMLhvgv47RGei4aNvZvQGK7i1jmdsXZtnrm',
            url='https://gateway-fra.watsonplatform.net/tone-analyzer/api',
        )

        translated_text = yaml.load(json.dumps(translated_text))  # decodes unicode dictionary. only cuz python2.7
        translated_text = translated_text['translations'][0]['translation']

        tone_analysis = tone_analyzer.tone(
            {'text': translated_text},
            content_type='application/json'
        ).get_result()
        print(json.dumps(tone_analysis, indent=2)).encode('utf8')
        return WorkoutController.analyze_emotion(tone_analysis)

    @staticmethod
    def analyze_emotion(tone_analysis):
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
                    return 3
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
    def check_context_in_text(spoken_text):
        pass # TODO: Implement this function

