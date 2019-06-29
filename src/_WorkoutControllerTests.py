# coding=utf-8
import json
from workout_controller import WorkoutController
import unittest


class WorkoutControllerTests(unittest.TestCase):

    def test_EmotionIntepret(self):
        json_string = '{"document_tone":' \
                      ' {"tones":' \
                      ' [{"score": 0.880435,' \
                      '"tone_id": "joy",' \
                      '"tone_name": "Joy"},' \
                      '{"score": 0.946222,' \
                      '"tone_id": "tentative",' \
                      '"tone_name": "Tentative"},' \
                      '{"score": 0.660207,' \
                      '"tone_id": "confident",' \
                      '"tone_name": "Confident"}]}}'

        json_dict = json.loads(json_string)
        result = WorkoutController._get_emotion_level_based_on_json(json_dict)
        self.assertIsNotNone(result)

    def test_WatsonToneAnalyzer(self):
        untranslated_text = "Ich fühle mich ziemlich gut."
        res = WorkoutController.analyze_emotion_by_text(untranslated_text)
        self.assertIsInstance(res, int)

    def test_ContextCheckWitAi(self):
        context = "Ehrlich ist gesagt wuerde ich nicht ein Workout von Alexa machen wollen."
        self.assert_(WorkoutController.check_context_wit_ai(context), "alexa_workout")

    def test_ContextbyOwn(self):
        context = "ich will ein leichtes Workout"
        self.assert_(WorkoutController.check_context_in_text(context,
                                                             ["leicht", "leichtes"],
                                                             ["schwer", "schweres"]),
                                                             ["leicht", "leichtes"])

    def test_YamlReadSpeeches(self):
        result = WorkoutController.get_speech("ssm_test")
        self.assertIsInstance(result, str)


if __name__ == '__main__':
    unittest.main()
