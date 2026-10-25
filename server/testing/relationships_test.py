from datetime import date

from models import Exercise, Workout, WorkoutExercise, db


# A helper that builds a small set of related data, so each test does not repeat the setup.
# It returns the objects so tests can check them.
def build_graph():
    # Three exercises: two strength and one core.
    squat = Exercise(name='Squat', category='strength', equipment_needed=True)
    row = Exercise(name='Row', category='strength', equipment_needed=True)
    plank = Exercise(name='Plank', category='core', equipment_needed=False)
    # Two workouts on the same day.
    morning = Workout(date=date(2026, 10, 24), duration_minutes=40)
    evening = Workout(date=date(2026, 10, 24), duration_minutes=20)
    db.session.add_all([squat, row, plank, morning, evening])
    db.session.commit()

    # Each entry links one workout to one exercise. Entries are how the two are connected.
    entries = [
        WorkoutExercise(workout=morning, exercise=squat, reps=8, sets=3, duration_seconds=180),
        WorkoutExercise(workout=morning, exercise=row, reps=10, sets=3, duration_seconds=150),
        WorkoutExercise(workout=evening, exercise=plank, reps=1, sets=2, duration_seconds=60),
    ]
    db.session.add_all(entries)
    db.session.commit()
    return squat, row, plank, morning, evening, entries


# Each test checks one relationship from the README. The name says what is being checked.
class TestRelationships:
    # "belongs to": an entry points back to its workout and its exercise.
    def test_workout_exercise_belongs_to_workout_and_exercise(self, app):
        squat, _, _, morning, _, entries = build_graph()
        assert entries[0].workout is morning
        assert entries[0].exercise is squat

    def test_workout_has_many_workout_exercises(self, app):
        _, _, _, morning, evening, _ = build_graph()
        assert len(morning.workout_exercises) == 2
        assert len(evening.workout_exercises) == 1

    def test_exercise_has_many_workout_exercises(self, app):
        squat, row, plank, _, _, _ = build_graph()
        assert len(squat.workout_exercises) == 1
        assert len(row.workout_exercises) == 1
        assert plank.workout_exercises[0].reps == 1

    # "Through" relationships skip the join table and jump straight from one model to the other.
    def test_workout_has_many_exercises_through_workout_exercises(self, app):
        squat, row, plank, morning, evening, _ = build_graph()
        assert set(morning.exercises) == {squat, row}
        assert evening.exercises == [plank]

    def test_exercise_has_many_workouts_through_workout_exercises(self, app):
        squat, _, _, morning, _, _ = build_graph()
        assert squat.workouts == [morning]

    # The same exercise can appear in more than one workout, so this test adds a second entry for squat.
    def test_shared_exercise_appears_in_each_workout(self, app):
        squat, _, _, morning, evening, _ = build_graph()
        db.session.add(WorkoutExercise(workout=evening, exercise=squat,
                                       reps=5, sets=5, duration_seconds=300))
        db.session.commit()
        # Squat now has two entries, so it shows up in both workouts.
        assert set(squat.workouts) == {morning, evening}
        assert len(db.session.get(Exercise, squat.id).workouts) == 2
        assert WorkoutExercise.query.count() == 4
