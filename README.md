# Workout Backend API

A Flask REST API for tracking workouts and the exercises performed in them. You can create and view exercises, create and view workouts, and add exercises to a workout with reps, sets, and duration. Deleting a workout or an exercise also removes its workout entries.

Data is stored in SQLite through Flask-SQLAlchemy, schema changes are managed with Flask-Migrate, and request and response data is validated and serialized with marshmallow.

## Features

- Create, list, view, and delete exercises
- Create, list, view, and delete workouts
- Add an exercise to a workout with `reps`, `sets`, and `duration_seconds`
- Validation at three levels: database constraints, model validations, and marshmallow schema validations
- Cascading deletes: removing a workout or an exercise removes its workout entries
- Seed script with sample exercises, workouts, and entries
- Pytest suite covering the API and model relationships

## Requirements

- Python 3.12
- Pipenv

## Installation

Run these commands from the project root, where the `Pipfile` is:

```bash
pipenv install --dev                    # install dependencies, including test tools
cd server
pipenv run flask --app app db upgrade   # create the database tables
pipenv run python seed.py               # optional: load sample exercises, workouts, and entries
```

The database is created at `server/instance/app.db`. To use a different database, set `DATABASE_URL` before running any command, for example `DATABASE_URL=sqlite:///other.db`.

## Running the API

From the `server/` directory:

```bash
pipenv run flask --app app run --port 5555
```

The API is then available at `http://127.0.0.1:5555`. Example request:

```bash
curl http://127.0.0.1:5555/exercises
```

## Endpoints

All request and response bodies are JSON. Responses for lists are arrays.

| Method | Path | Description | Success |
| ------ | ---- | ----------- | ------- |
| GET | `/exercises` | List all exercises, ordered by `id` | 200 |
| POST | `/exercises` | Create an exercise | 201 |
| GET | `/exercises/<id>` | View one exercise | 200 |
| DELETE | `/exercises/<id>` | Delete an exercise and its workout entries | 200 |
| GET | `/workouts` | List all workouts, ordered by `id`, each with its entries | 200 |
| POST | `/workouts` | Create a workout | 201 |
| GET | `/workouts/<id>` | View one workout with its exercise entries | 200 |
| DELETE | `/workouts/<id>` | Delete a workout and its exercise entries | 200 |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout | 201 |

### Endpoint details

**`GET /exercises`** returns an array of exercises.

**`POST /exercises`** creates an exercise. Request body:

```json
{ "name": "Push-up", "category": "strength", "equipment_needed": false }
```

Response: the created exercise, including its `id`.

**`GET /exercises/<id>`** returns one exercise, or 404 if it does not exist.

**`DELETE /exercises/<id>`** deletes the exercise and every workout entry that uses it. Response: `{ "message": "Exercise deleted" }`.

**`GET /workouts`** returns an array of workouts. Each item has the same shape as `GET /workouts/<id>` below, including its `workout_exercises`.

**`POST /workouts`** creates a workout. Request body:

```json
{ "date": "2026-10-24", "duration_minutes": 40, "notes": "Leg day" }
```

`notes` is optional. Response: the created workout, with an empty `workout_exercises` list.

**`GET /workouts/<id>`** returns one workout with its entries under `workout_exercises`. Each entry has `id`, `workout_id`, `exercise_id`, `reps`, `sets`, and `duration_seconds`. Returns 404 if the workout does not exist.

```json
{
  "id": 1,
  "date": "2026-10-24",
  "duration_minutes": 40,
  "notes": "Leg day",
  "workout_exercises": [
    { "id": 1, "workout_id": 1, "exercise_id": 2, "reps": 8, "sets": 3, "duration_seconds": 180 }
  ]
}
```

**`DELETE /workouts/<id>`** deletes the workout and its entries. Response: `{ "message": "Workout deleted" }`.

**`POST /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises`** adds an exercise to a workout. The workout and exercise come from the path, so any `workout_id` or `exercise_id` in the body is ignored. Request body:

```json
{ "reps": 8, "sets": 3, "duration_seconds": 180 }
```

Response: the full workout, including the new entry in `workout_exercises`. Returns 404 if either the workout or the exercise does not exist.

### Field rules

| Resource | Field | Rule |
| -------- | ----- | ---- |
| Exercise | `name` | Required, 1–100 characters, not blank, unique |
| Exercise | `category` | Required, 1–50 characters, not blank |
| Exercise | `equipment_needed` | Required boolean |
| Workout | `date` | Required, `YYYY-MM-DD` |
| Workout | `duration_minutes` | Required integer, 1–1440 |
| Workout | `notes` | Optional text, up to 2000 characters |
| Workout entry | `reps` | Required integer, 1–10000 |
| Workout entry | `sets` | Required integer, 1–100 |
| Workout entry | `duration_seconds` | Required integer, 1–86400 |

### Error responses

| Status | When | Body |
| ------ | ---- | ---- |
| 400 | Schema validation fails | `{ "errors": { "field": ["message"] } }` |
| 400 | Model validation fails | `{ "error": "message" }` |
| 404 | Workout or exercise does not exist | `{ "error": "Workout not found" }` |
| 409 | A database constraint is violated, such as a duplicate exercise name | `{ "error": "Request conflicts with an existing record or database constraint" }` |

## Testing

Run the test suite from the `server/` directory:

```bash
pipenv run pytest
```

Tests use an in-memory SQLite database, so they do not touch `instance/app.db`. The suite has 24 tests:

- `server/testing/api_test.py`: endpoint behavior, validation errors, and cascading deletes
- `server/testing/relationships_test.py`: model relationships, including the `Workout.exercises` and `Exercise.workouts` through-relationships
- `server/testing/conftest.py`: shared fixtures for the test app and client

## Project structure

```
.
├── Pipfile                  # dependencies
├── Pipfile.lock             # locked dependency versions
├── README.md
└── server/
    ├── app.py               # Flask app, routes, and error handlers
    ├── models.py            # SQLAlchemy models, constraints, and model validations
    ├── schemas.py           # marshmallow schemas and schema validations
    ├── seed.py              # sample data for all models
    ├── pytest.ini
    ├── migrations/          # Flask-Migrate migration scripts
    └── testing/             # pytest test files
```

## Dependencies

Dependencies are listed in the [Pipfile](Pipfile):

| Package | Version | Purpose |
| ------- | ------- | ------- |
| flask | 2.2.2 | Web framework |
| flask-migrate | 3.1.0 | Database migrations |
| flask-sqlalchemy | 3.0.3 | ORM integration |
| werkzeug | 2.2.2 | WSGI utilities |
| marshmallow | 3.20.1 | Serialization and validation |
| importlib-metadata | 6.0.0 | Pinned to the assignment's required version |
| importlib-resources | 5.10.0 | Pinned to the assignment's required version |

Dev packages: `pytest` (tests) and `ipdb` (debugging).

## Assignment Brief

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





