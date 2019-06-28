from workout_controller import WorkoutController


def main():
    """

    :return:
    """

    wc = WorkoutController()

    alexa_workout = wc.get_workout_by_alexa(1, 2)

    print(alexa_workout)


if __name__ == '__main__':
    main()
