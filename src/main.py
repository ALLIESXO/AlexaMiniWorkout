from workout_controller import WorkoutController


def main():
    # Nur zum testen

    wc = WorkoutController()
    # workout = wc.get_workout_by_name("Forces of Nature")
    # print(workout['workout'])
    print(wc.get_workout_by_user(3,14,0,0))
    print(wc.get_workout_by_alexa(1, 2))


if __name__ == '__main__':
    main()
