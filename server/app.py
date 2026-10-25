#!/usr/bin/env python3

# This file creates the Flask app and defines every URL (route) the API responds to.

import os

# Flask builds the web server. Flask-Migrate handles database table changes.
# EXCLUDE and ValidationError come from marshmallow, which checks incoming data.
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import EXCLUDE, ValidationError
from sqlalchemy.exc import IntegrityError

# The models describe the database tables. The schemas convert data to and from JSON.
from models import db, Exercise, Workout, WorkoutExercise
from schemas import ExerciseSchema, WorkoutExerciseSchema, WorkoutSchema

# Create the app. Flask uses this object to register each route below.
app = Flask(__name__)

# Use the DATABASE_URL environment variable if it is set. Otherwise, use a file named app.db.
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
# Turn off a feature that tracks object changes. The API doesn't need it, and it uses extra memory.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Print JSON with one field per line so responses are easy to read.
app.json.compact = False

# Connect Flask-Migrate to the app, and connect the database (db) to the app.
migrate = Migrate(app, db)
db.init_app(app)

# Schema objects convert data in both directions:
#   .dump() turns a model object into a dictionary that can become JSON.
#   .load() checks incoming JSON and turns it into a dictionary the models can use.
# The "many=True" versions handle a list of items instead of one item.
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()


# Error handlers turn Python errors into JSON responses with a status code.
# The client gets a clear message instead of a server crash.
@app.errorhandler(ValidationError)
def handle_schema_validation_error(err):
    # The schema rejected the incoming data, for example a blank name.
    return jsonify({'errors': err.messages}), 400


@app.errorhandler(ValueError)
def handle_model_validation_error(err):
    # A model rejected a value. The message comes from the check in models.py.
    return jsonify({'error': str(err)}), 400


@app.errorhandler(IntegrityError)
def handle_integrity_error(err):
    # The database refused the change, such as a duplicate exercise name.
    # Roll back undoes the failed change so the session can be used again.
    db.session.rollback()
    return jsonify({'error': 'Request conflicts with an existing record or database constraint'}), 409


def _json_body():
    # Read the JSON sent by the client. silent=True returns None instead of crashing
    # when the body isn't valid JSON. "or {}" turns None into an empty dictionary.
    return request.get_json(silent=True) or {}


def _get_or_404(model, record_id, label):
    # Find one row by its id. The function returns two values: (record, None) when
    # the row exists, or (None, error response) when it doesn't. Each route checks
    # the second value and returns early if it is set.
    record = db.session.get(model, record_id)
    if record is None:
        return None, (jsonify({'error': f'{label} not found'}), 404)
    return record, None


# Each route is a function. The line above it (for example @app.get('/exercises'))
# says which HTTP method and URL the function handles.
# Status codes: 200 = OK, 201 = created, 400 = bad request, 404 = not found, 409 = conflict.


@app.get('/exercises')
def get_exercises():
    # Get all exercises, sorted by id, and return them as a JSON list.
    exercises = Exercise.query.order_by(Exercise.id).all()
    return jsonify(exercises_schema.dump(exercises)), 200


@app.post('/exercises')
def create_exercise():
    # load() checks the data first. Bad data raises ValidationError, which is handled above.
    data = exercise_schema.load(_json_body())
    exercise = Exercise(**data)
    # add() stages the new row. commit() saves it to the database.
    db.session.add(exercise)
    db.session.commit()
    return jsonify(exercise_schema.dump(exercise)), 201


@app.get('/exercises/<int:exercise_id>')
def get_exercise(exercise_id):
    # The <int:exercise_id> part of the URL is read as a whole number and passed in here.
    exercise, error = _get_or_404(Exercise, exercise_id, 'Exercise')
    if error:
        return error
    return jsonify(exercise_schema.dump(exercise)), 200


@app.delete('/exercises/<int:exercise_id>')
def delete_exercise(exercise_id):
    exercise, error = _get_or_404(Exercise, exercise_id, 'Exercise')
    if error:
        return error
    # Deleting the exercise also deletes its workout entries. models.py sets up this cascade.
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({'message': 'Exercise deleted'}), 200


@app.get('/workouts')
def get_workouts():
    # Get all workouts, sorted by id. Each one includes its exercise entries.
    workouts = Workout.query.order_by(Workout.id).all()
    return jsonify(workouts_schema.dump(workouts)), 200


@app.post('/workouts')
def create_workout():
    data = workout_schema.load(_json_body())
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return jsonify(workout_schema.dump(workout)), 201


@app.get('/workouts/<int:workout_id>')
def get_workout(workout_id):
    workout, error = _get_or_404(Workout, workout_id, 'Workout')
    if error:
        return error
    return jsonify(workout_schema.dump(workout)), 200


@app.delete('/workouts/<int:workout_id>')
def delete_workout(workout_id):
    workout, error = _get_or_404(Workout, workout_id, 'Workout')
    if error:
        return error
    # Deleting the workout also deletes its exercise entries. models.py sets up this cascade.
    db.session.delete(workout)
    db.session.commit()
    return jsonify({'message': 'Workout deleted'}), 200


@app.post('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises')
def add_exercise_to_workout(workout_id, exercise_id):
    # Both ids come from the URL. If either row is missing, _get_or_404 returns a 404 response.
    workout, error = _get_or_404(Workout, workout_id, 'Workout')
    if error:
        return error
    exercise, error = _get_or_404(Exercise, exercise_id, 'Exercise')
    if error:
        return error
    # The path identifies the workout and exercise, so body values for those are ignored.
    data = workout_exercise_schema.load(_json_body(), unknown=EXCLUDE)
    # Passing workout= and exercise= objects sets both foreign keys (the links to those rows).
    workout_exercise = WorkoutExercise(workout=workout, exercise=exercise, **data)
    db.session.add(workout_exercise)
    db.session.commit()
    # Return the whole workout so the client can see the new entry in its list.
    return jsonify(workout_schema.dump(workout)), 201


# Runs the server when you start this file directly with "python app.py".
# "flask run" does not use this block.
if __name__ == '__main__':
    app.run(port=5555, debug=True)
