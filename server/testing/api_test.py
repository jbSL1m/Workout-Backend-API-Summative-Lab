from datetime import date

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from models import Exercise, Workout, WorkoutExercise, db


# The tests call the real routes through the fake client and check the status codes and JSON.
# Helper functions below create data through the API, so each test starts with the same setup.
# This helper creates an exercise and asserts it was created, so tests can rely on it.
def make_exercise(client, name='Squat', category='strength', equipment_needed=False):
    response = client.post('/exercises', json={
        'name': name,
        'category': category,
        'equipment_needed': equipment_needed,
    })
    assert response.status_code == 201
    return response.get_json()


# Helper that creates a workout through POST /workouts. Notes are always 'Leg day' here.
def make_workout(client, duration_minutes=45):
    response = client.post('/workouts', json={
        'date': '2026-10-24',
        'duration_minutes': duration_minutes,
        'notes': 'Leg day',
    })
    assert response.status_code == 201
    return response.get_json()


# Each class groups tests for one resource. Test names describe what the test checks.
class TestExercises:
    # Create an exercise, then read it back by id.
    def test_creates_and_views_exercise(self, client):
        exercise = make_exercise(client)
        assert exercise['name'] == 'Squat'

        response = client.get(f"/exercises/{exercise['id']}")
        assert response.status_code == 200
        assert response.get_json()['category'] == 'strength'

    # A blank name passes the length check, so the custom validator in the schema must catch it.
    def test_schema_rejects_blank_name(self, client):
        response = client.post('/exercises', json={
            'name': '   ', 'category': 'strength', 'equipment_needed': False,
        })
        assert response.status_code == 400
        assert 'name' in response.get_json()['errors']

    # The database has a UNIQUE rule on name. The second insert breaks it, and the app returns 409.
    def test_duplicate_name_violates_unique_constraint(self, client):
        make_exercise(client, name='Plank')
        response = client.post('/exercises', json={
            'name': 'Plank', 'category': 'core', 'equipment_needed': False,
        })
        assert response.status_code == 409

    # pytest.raises(ValueError) passes only if the block raises a ValueError. This checks the model's own check.
    def test_model_rejects_non_boolean_equipment(self, app):
        with pytest.raises(ValueError):
            Exercise(name='Row', category='cardio', equipment_needed='yes')

    # Deleting an exercise that has no entries should just remove it.
    def test_deletes_unused_exercise(self, client):
        exercise = make_exercise(client)
        response = client.delete(f"/exercises/{exercise['id']}")
        assert response.status_code == 200
        assert client.get(f"/exercises/{exercise['id']}").status_code == 404

    # Cascade check: deleting the exercise also deletes its entries, but the workout itself stays.
    def test_deleting_exercise_removes_its_workout_entries(self, client):
        exercise = make_exercise(client)
        workout = make_workout(client)
        setup = client.post(
            f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
            json={'reps': 10, 'sets': 3, 'duration_seconds': 120},
        )
        assert setup.status_code == 201
        response = client.delete(f"/exercises/{exercise['id']}")
        assert response.status_code == 200
        assert client.get(f"/exercises/{exercise['id']}").status_code == 404
        remaining = client.get(f"/workouts/{workout['id']}")
        assert remaining.status_code == 200
        assert remaining.get_json()['workout_exercises'] == []


# Workout tests cover the same three kinds of checks: the endpoint, the schema, and the model and database.
class TestWorkouts:
    def test_creates_and_views_workout(self, client):
        workout = make_workout(client)
        response = client.get(f"/workouts/{workout['id']}")
        assert response.status_code == 200
        assert response.get_json()['date'] == '2026-10-24'

    # The schema checks the number before the model or database sees it.
    def test_schema_rejects_zero_duration(self, client):
        response = client.post('/workouts', json={
            'date': '2026-10-24', 'duration_minutes': 0,
        })
        assert response.status_code == 400
        assert 'duration_minutes' in response.get_json()['errors']

    def test_model_rejects_zero_duration(self, app):
        # The model's own check should raise ValueError, even without going through the API.
        with pytest.raises(ValueError):
            Workout(date=date(2026, 10, 24), duration_minutes=0)

    # This test writes raw SQL, which skips the Python checks. Only the database CHECK rule can stop it.
    # db.session.rollback() undoes the failed insert so later tests are not affected.
    def test_database_rejects_zero_duration(self, app):
        with pytest.raises(IntegrityError):
            db.session.execute(text(
                "INSERT INTO workouts (date, duration_minutes) VALUES ('2026-10-24', 0)"
            ))
        db.session.rollback()

    # Deleting a workout should also delete its entries. The exercise is kept, because it is not part of the workout.
    def test_delete_workout_removes_its_exercise_entries(self, client):
        exercise = make_exercise(client)
        workout = make_workout(client)
        setup = client.post(
            f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
            json={'reps': 8, 'sets': 4, 'duration_seconds': 60},
        )
        assert setup.status_code == 201
        assert client.delete(f"/workouts/{workout['id']}").status_code == 200
        assert WorkoutExercise.query.count() == 0
        assert Exercise.query.count() == 1

    def test_missing_workout_returns_404(self, client):
        assert client.get('/workouts/999').status_code == 404


# Entry tests: adding an exercise to a workout through the nested URL.
class TestWorkoutExercises:
    def test_adds_exercise_to_workout(self, client):
        exercise = make_exercise(client)
        workout = make_workout(client)
        response = client.post(
            f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
            json={'reps': 10, 'sets': 3, 'duration_seconds': 90},
        )
        assert response.status_code == 201
        entries = response.get_json()['workout_exercises']
        assert len(entries) == 1
        assert entries[0]['reps'] == 10
        assert entries[0]['exercise_id'] == exercise['id']

    # @pytest.mark.parametrize runs the same test once for each row: field name and bad value.
    @pytest.mark.parametrize('field, value', [
        ('reps', 0), ('sets', 0), ('duration_seconds', -5),
    ])
    def test_schema_rejects_non_positive_values(self, client, field, value):
        exercise = make_exercise(client)
        workout = make_workout(client)
        body = {'reps': 10, 'sets': 3, 'duration_seconds': 90}
        body[field] = value
        response = client.post(
            f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
            json=body,
        )
        assert response.status_code == 400
        assert field in response.get_json()['errors']

    def test_unknown_exercise_returns_404(self, client):
        workout = make_workout(client)
        response = client.post(
            f"/workouts/{workout['id']}/exercises/999/workout_exercises",
            json={'reps': 10, 'sets': 3, 'duration_seconds': 90},
        )
        assert response.status_code == 404

    # Raw SQL bypasses the Python checks, so this test proves the database CHECK on reps also works.
    def test_database_rejects_non_positive_reps(self, app, client):
        exercise = make_exercise(client)
        workout = make_workout(client)
        with pytest.raises(IntegrityError):
            db.session.execute(text(
                'INSERT INTO workout_exercises (workout_id, exercise_id, reps, sets, duration_seconds) '
                f'VALUES ({workout["id"]}, {exercise["id"]}, 0, 3, 90)'
            ))
        db.session.rollback()
