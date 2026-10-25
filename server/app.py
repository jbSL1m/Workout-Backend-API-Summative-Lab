#!/usr/bin/env python3

import os

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import ExerciseSchema, WorkoutExerciseSchema, WorkoutSchema

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()


@app.errorhandler(ValidationError)
def handle_schema_validation_error(err):
    return jsonify({'errors': err.messages}), 400


@app.errorhandler(ValueError)
def handle_model_validation_error(err):
    return jsonify({'error': str(err)}), 400


@app.errorhandler(IntegrityError)
def handle_integrity_error(err):
    db.session.rollback()
    return jsonify({'error': 'Request conflicts with an existing record or database constraint'}), 409


def _json_body():
    return request.get_json(silent=True) or {}


def _get_or_404(model, record_id, label):
    record = db.session.get(model, record_id)
    if record is None:
        return None, (jsonify({'error': f'{label} not found'}), 404)
    return record, None


@app.get('/exercises')
def get_exercises():
    exercises = Exercise.query.order_by(Exercise.id).all()
    return jsonify(exercises_schema.dump(exercises)), 200


@app.post('/exercises')
def create_exercise():
    data = exercise_schema.load(_json_body())
    exercise = Exercise(**data)
    db.session.add(exercise)
    db.session.commit()
    return jsonify(exercise_schema.dump(exercise)), 201


@app.get('/exercises/<int:exercise_id>')
def get_exercise(exercise_id):
    exercise, error = _get_or_404(Exercise, exercise_id, 'Exercise')
    if error:
        return error
    return jsonify(exercise_schema.dump(exercise)), 200


@app.delete('/exercises/<int:exercise_id>')
def delete_exercise(exercise_id):
    exercise, error = _get_or_404(Exercise, exercise_id, 'Exercise')
    if error:
        return error
    # Workouts may not lose an exercise, so an exercise in use cannot be deleted.
    if exercise.workout_exercises:
        return jsonify({'error': 'Exercise is used in one or more workouts and cannot be deleted'}), 409
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({'message': 'Exercise deleted'}), 200


@app.get('/workouts')
def get_workouts():
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
    db.session.delete(workout)
    db.session.commit()
    return jsonify({'message': 'Workout deleted'}), 200


@app.post('/workouts/<int:workout_id>/exercises')
def add_exercise_to_workout(workout_id):
    workout, error = _get_or_404(Workout, workout_id, 'Workout')
    if error:
        return error
    data = workout_exercise_schema.load(_json_body())
    _, error = _get_or_404(Exercise, data['exercise_id'], 'Exercise')
    if error:
        return error
    workout_exercise = WorkoutExercise(workout=workout, **data)
    db.session.add(workout_exercise)
    db.session.commit()
    return jsonify(workout_schema.dump(workout)), 201


if __name__ == '__main__':
    app.run(port=5555, debug=True)
