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




