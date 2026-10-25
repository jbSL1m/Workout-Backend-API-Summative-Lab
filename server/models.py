# Models are Python classes that match the database tables.
# Each class becomes one table, and each db.Column becomes one column in that table.

from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, MetaData
from sqlalchemy.orm import validates

# Naming conventions give every constraint a predictable name in migrations.
metadata = MetaData(naming_convention={
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
})

# db connects Python to the database. Every model class inherits from db.Model.
db = SQLAlchemy(metadata=metadata)


# Helper: raises an error if a text value is empty or only spaces.
# It returns the text with extra spaces removed from both ends.
def _require_text(value, field):
    if value is None or not str(value).strip():
        raise ValueError(f'{field} must not be blank')
    return value.strip()


# Helper: accepts only whole numbers above zero.
# True and False are rejected, even though Python treats them as numbers.
def _require_positive_int(value, field):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f'{field} must be a positive integer')
    return value


# An exercise is one movement, such as a push-up or a squat.
class Exercise(db.Model):
    # __tablename__ sets the name of the table in the database.
    __tablename__ = 'exercises'
    # CHECK constraints: the database itself refuses rows that break these rules.
    __table_args__ = (
        CheckConstraint('length(trim(name)) > 0', name='name_not_blank'),
        CheckConstraint('length(trim(category)) > 0', name='category_not_blank'),
    )

    # primary_key=True: each row gets a unique id, which the database fills in.
    # unique=True: no two exercises can have the same name.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # A relationship lets Python reach linked rows, like exercise.workout_exercises.
    # cascade='all, delete-orphan' means deleting this exercise also deletes its entries.
    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='exercise',
        cascade='all, delete-orphan',
    )
    # viewonly=True: this list can be read but not changed directly.
    # To add a workout entry, create a WorkoutExercise object instead.
    workouts = db.relationship('Workout', secondary='workout_exercises', viewonly=True)

    # @validates runs this function every time name is set. It checks the value before it is saved.
    @validates('name')
    def validate_name(self, key, value):
        return _require_text(value, 'name')

    @validates('category')
    def validate_category(self, key, value):
        return _require_text(value, 'category')

    @validates('equipment_needed')
    def validate_equipment_needed(self, key, value):
        if not isinstance(value, bool):
            raise ValueError('equipment_needed must be a boolean')
        return value

    # __repr__ controls how the object looks when printed. It helps when debugging.
    def __repr__(self):
        return f'<Exercise {self.id}, {self.name}>'


# A workout is one training session on one date.
class Workout(db.Model):
    __tablename__ = 'workouts'
    # The database refuses zero or negative minutes, even if the Python checks are skipped.
    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='duration_minutes_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    # Text has no length limit. Notes are optional because the column allows empty values.
    notes = db.Column(db.Text)

    # Deleting a workout also deletes its exercise entries.
    # cascade='all, delete-orphan' tells SQLAlchemy to do this for us.
    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='workout',
        cascade='all, delete-orphan',
    )
    # "secondary" means the link goes through the workout_exercises table.
    # This gives the exercises in a workout without storing them directly on the workout.
    exercises = db.relationship('Exercise', secondary='workout_exercises', viewonly=True)

    @validates('date')
    def validate_date(self, key, value):
        if not isinstance(value, date):
            raise ValueError('date must be a date')
        return value

    @validates('duration_minutes')
    def validate_duration_minutes(self, key, value):
        return _require_positive_int(value, 'duration_minutes')

    def __repr__(self):
        return f'<Workout {self.id}, {self.date}, {self.duration_minutes} min>'


# The join table. Each row links one workout to one exercise and stores
# the reps, sets, and duration for that pairing. This connects workouts and exercises,
# where one workout can have many exercises and one exercise can be in many workouts.
class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'
    # These CHECK rules keep the numbers above zero inside the database itself.
    __table_args__ = (
        CheckConstraint('reps > 0', name='reps_positive'),
        CheckConstraint('sets > 0', name='sets_positive'),
        CheckConstraint('duration_seconds > 0', name='duration_seconds_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    # A foreign key stores the id of a row in another table, which links the two rows.
    # This column must match an id in the workouts table.
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=False)

    # Lets you reach the workout from an entry, like entry.workout.
    # back_populates keeps both sides of the link in sync.
    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    @validates('reps')
    def validate_reps(self, key, value):
        return _require_positive_int(value, 'reps')

    @validates('sets')
    def validate_sets(self, key, value):
        return _require_positive_int(value, 'sets')

    @validates('duration_seconds')
    def validate_duration_seconds(self, key, value):
        return _require_positive_int(value, 'duration_seconds')

    def __repr__(self):
        return f'<WorkoutExercise {self.id}, workout {self.workout_id}, exercise {self.exercise_id}>'
