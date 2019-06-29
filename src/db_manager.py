import sqlite3
from sqlite3 import Error


class DbManager:

    def create_connection(self, db_file):
        """ create a database connection to the SQLite database
            specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)

        return None

    def get_connection(self):
        """
        Returns a new Connection to the database
        :return: the connection
        """

        database = "db/alexa_workout.db"

        # create a database connection
        conn = self.create_connection(database)
        return conn

    def select_workout_by_name(self, name):
        """
        get a workout and all exercises by the name of the workout
        :param name:
        :return: workout and exercises as json
        """
        conn = self.get_connection()

        with conn:
            cur = conn.cursor()
            result = cur.execute("SELECT ex.id, ex.name,ex.description, ex.difficulty, ex.body_part FROM workouts as w "
                                 "JOIN workout_exercises as we ON w.id = we.workout_id "
                                 "JOIN exercises as ex ON we.exercise_id = ex.id "
                                 "WHERE w.name like ?", (name,))

            exercises = [dict(zip([key[0] for key in cur.description], row)) for row in result]

            cur = conn.cursor()
            result = cur.execute("SELECT * FROM workouts as w "
                                 "WHERE w.name like ?", (name,))

            workouts = [dict(zip([key[0] for key in cur.description], row)) for row in result]

            workout = {"workout": workouts, "exercises": exercises}

            return workout

    def select_workout_by_id(self, id):
        """
        get a workout and all exercises by the id of the workout
        :param name:
        :return: workout and exercises as json
        """
        conn = self.get_connection()

        with conn:
            cur = conn.cursor()
            result = cur.execute("SELECT ex.id, ex.name,ex.description, ex.difficulty, ex.body_part FROM workouts as w "
                                 "JOIN workout_exercises as we ON w.id = we.workout_id "
                                 "JOIN exercises as ex ON we.exercise_id = ex.id "
                                 "WHERE w.id like ?", (id,))

            exercises = [dict(zip([key[0] for key in cur.description], row)) for row in result]

            cur = conn.cursor()
            result = cur.execute("SELECT * FROM workouts as w "
                                 "WHERE w.id like ?", (id,))

            workouts = [dict(zip([key[0] for key in cur.description], row)) for row in result]

            workout = {"workout": workouts, "exercises": exercises}

            return workout

    def select_workout_by_intensity_and_bodypart(self, intensity, body_part):
        """
        get a workout and all its exercises by its intensity and body part
        :param intensity:
        :param body_part:
        :return: the workout and its exercises as json
        """
        conn = self.get_connection()
        workouts_to_return = []

        with conn:
            cur = conn.cursor()
            result = cur.execute("SELECT * from workouts as w WHERE w.intensity = ? AND w.body_part = ?",
                                 (intensity, body_part))
            workouts = [dict(zip([key[0] for key in cur.description], row)) for row in result]

            for row in workouts:
                cur = conn.cursor()
                result = cur.execute(
                    "SELECT ex.id, ex.name,ex.description, ex.difficulty, ex.body_part FROM workouts as w "
                    "JOIN workout_exercises as we ON w.id = we.workout_id "
                    "JOIN exercises as ex ON we.exercise_id = ex.id "
                    "WHERE w.id = ?", (row['id'],))
                exercises = [dict(zip([key[0] for key in cur.description], row)) for row in result]
                workout = {"workout": row, "exercises": exercises}
                workouts_to_return.append(workout)

        return workouts_to_return

    def select_workouts_by_user_parameters(self, intensity):
        """
        get all workouts by the parameters defined by the user
        :param intensity:
        :return:
        """
        conn = self.get_connection()
        workouts_to_return = []

        with conn:
            cur = conn.cursor()
            result = cur.execute(
                "SELECT * from workouts as w WHERE w.intensity = ?", (intensity,))
            workouts = [dict(zip([key[0] for key in cur.description], row)) for row in result]

            for workout_row in workouts:
                cur = conn.cursor()
                result = cur.execute(
                    "SELECT ex.id, ex.name,ex.description, ex.difficulty, ex.body_part FROM workouts as w "
                    "JOIN workout_exercises as we ON w.id = we.workout_id "
                    "JOIN exercises as ex ON we.exercise_id = ex.id "
                    "WHERE w.id = ?", (workout_row['id'],))
                exercises = [dict(zip([key[0] for key in cur.description], row)) for row in result]
                workout = {"workout": workout_row, "exercises": exercises}
                workouts_to_return.append(workout)

        return workouts_to_return

    def get_last_user_workout(self, user_id):
        """
        Returns the last done workout of the user
        :param user_id:
        :return:
        """

        conn = self.get_connection()

        with conn:
            cur = conn.cursor()
            result = cur.execute("SELECT * from user_workouts as uw WHERE uw.user_id = ? order by uw.id desc",
                                 (user_id,))
            workouts = [dict(zip([key[0] for key in cur.description], row)) for row in result]

        if workouts.__len__() > 0:
            return workouts[0]
        else:
            return []

    def get_last_user_workouts(self, user_id):
        """
        Returns all done workouts of a user by its id
        :param user_id:
        :return:
        """

        conn = self.get_connection()

        with conn:
            cur = conn.cursor()
            result = cur.execute("SELECT * from user_workouts as uw WHERE uw.user_id = ? order by uw.id desc",
                                 (user_id,))

            workouts = [dict(zip([key[0] for key in cur.description], row)) for row in result]

        if workouts.__len__() > 0:

            return workouts
        else:
            return []

    def get_user_fitness_ratings_array(self, user_id):
        """
        Returns all done workouts of a user by its id
        :param user_id:
        :return:
        """

        conn = self.get_connection()

        with conn:
            cur = conn.cursor()
            result = cur.execute("SELECT daily_form from user_workouts as uw WHERE uw.user_id = ? ",
                                 (user_id,))

            ratings = result.fetchall()

        if ratings.__len__() > 0:
            return ratings
        else:
            return []
