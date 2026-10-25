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

db = SQLAlchemy(metadata=metadata)


def _require_text(value, field):
    if value is None or not str(value).strip():
        raise ValueError(f'{field} must not be blank')
    return value.strip()


def _require_positive_int(value, field):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f'{field} must be a positive integer')
    return value


class Exercise(db.Model):
    __tablename__ = 'exercises'
    __table_args__ = (
        CheckConstraint('length(trim(name)) > 0', name='name_not_blank'),
        CheckConstraint('length(trim(category)) > 0', name='category_not_blank'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # Deleting an exercise deletes its workout entries as well.
    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='exercise',
        cascade='all, delete-orphan',
    )
    # Read-only: add entries through WorkoutExercise so reps, sets, and duration are set.
    workouts = db.relationship('Workout', secondary='workout_exercises', viewonly=True)

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

    def __repr__(self):
        return f'<Exercise {self.id}, {self.name}>'


class Workout(db.Model):
    __tablename__ = 'workouts'
    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='duration_minutes_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # Deleting a workout deletes its exercise entries as well.
    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='workout',
        cascade='all, delete-orphan',
    )
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


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'
    __table_args__ = (
        CheckConstraint('reps > 0', name='reps_positive'),
        CheckConstraint('sets > 0', name='sets_positive'),
        CheckConstraint('duration_seconds > 0', name='duration_seconds_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=False)

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
