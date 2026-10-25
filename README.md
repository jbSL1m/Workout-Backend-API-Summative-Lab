# Workout-Backend-API-Summative-Lab

Tools and Resources
Python 3.12
Text Editor or IDE (e.g., VS Code)
Git + GitHub
Pipenv
The following Python packages (for your Pipfile):
Flask = "2.2.2"
Flask-Migrate = "3.1.0"
flask-sqlalchemy = "3.0.3"
Werkzeug = "2.2.2"
importlib-metadata = "6.0.0"
importlib-resources = "5.10.0"
ipdb = "0.13.9"
marshmallow = "3.20.1"

TASK 1

Design an API that enables:

Creation, deletion, and viewing of workouts.
Creation, deletion, and viewing of Exercises.
Adding exercise to a workout.
Note, for this application, you do not need to implement any update actions. You also do not need to allow a user to remove an exercise from a workout; just add one.

Your API should have validations on the model and schema level, including database constraints. It’s up to you to determine what validations you want to include; you will be evaluated based on having more than one working validation in each of the following:

Table Constraints
Model Validations
Schema Validations

TASK 2 DETERMINE DESIGN

Entities: 

Exercise
id (integer, primary key)
name (string)
category (string)
equipment_needed (boolean)
Workout
id (integer, primary key)
date (date)
duration_minutes (integer)
notes (text)
WorkoutExercises (Join Table)
id (primary key)
workout_id (foreign key to Workout)
exercise_id (foreign key to Exercise)
reps (integer)
sets (integer)
duration_seconds (integer)





## Getting Started

```bash
pipenv install --dev
cd server
pipenv run flask --app app db upgrade   # create the database tables
pipenv run python seed.py               # optional: load sample exercises and workouts
pipenv run flask --app app run --port 5555
```

Run the tests from the `server/` directory:

```bash
pipenv run pytest
```

### Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/exercises` | List exercises |
| POST | `/exercises` | Create an exercise |
| GET | `/exercises/<id>` | View an exercise |
| DELETE | `/exercises/<id>` | Delete an exercise and its workout entries |
| GET | `/workouts` | List workouts |
| POST | `/workouts` | Create a workout |
| GET | `/workouts/<id>` | View a workout with its exercises |
| DELETE | `/workouts/<id>` | Delete a workout and its exercise entries |
| POST | `/workouts/<id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout with `reps`, `sets`, and `duration_seconds` |
