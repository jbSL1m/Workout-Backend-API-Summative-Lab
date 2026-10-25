#!/usr/bin/env python3

from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():

    # Clear existing rows so running this script again creates the same sample data.
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    exercises = {
        'Push-up': Exercise(name='Push-up', category='strength', equipment_needed=False),
        'Barbell Squat': Exercise(name='Barbell Squat', category='strength', equipment_needed=True),
        'Dumbbell Row': Exercise(name='Dumbbell Row', category='strength', equipment_needed=True),
        'Plank': Exercise(name='Plank', category='core', equipment_needed=False),
        'Jumping Jack': Exercise(name='Jumping Jack', category='cardio', equipment_needed=False),
        'Treadmill Run': Exercise(name='Treadmill Run', category='cardio', equipment_needed=True),
        'Cat-Cow Stretch': Exercise(name='Cat-Cow Stretch', category='flexibility', equipment_needed=False),
    }
    db.session.add_all(exercises.values())
    db.session.commit()

    full_body = Workout(date=date(2026, 10, 19), duration_minutes=45, notes='Full body strength')
    core_cardio = Workout(date=date(2026, 10, 21), duration_minutes=30, notes='Core and cardio')
    quick_run = Workout(date=date(2026, 10, 23), duration_minutes=25, notes='Easy recovery run')

    # Each entry links one workout to one exercise with its sets, reps, and time.
    WorkoutExercise(workout=full_body, exercise=exercises['Barbell Squat'],
                    reps=8, sets=4, duration_seconds=240)
    WorkoutExercise(workout=full_body, exercise=exercises['Push-up'],
                    reps=12, sets=3, duration_seconds=120)
    WorkoutExercise(workout=full_body, exercise=exercises['Dumbbell Row'],
                    reps=10, sets=3, duration_seconds=150)

    # Reps must be positive, so a timed plank is recorded as a single rep.
    WorkoutExercise(workout=core_cardio, exercise=exercises['Plank'],
                    reps=1, sets=3, duration_seconds=60)
    WorkoutExercise(workout=core_cardio, exercise=exercises['Jumping Jack'],
                    reps=30, sets=3, duration_seconds=90)
    WorkoutExercise(workout=core_cardio, exercise=exercises['Cat-Cow Stretch'],
                    reps=10, sets=2, duration_seconds=120)

    WorkoutExercise(workout=quick_run, exercise=exercises['Treadmill Run'],
                    reps=1, sets=1, duration_seconds=1200)

    db.session.add_all([full_body, core_cardio, quick_run])
    db.session.commit()
