# marshmallow schemas do two jobs:
#   dump: turn Python data into a dictionary that can become JSON for the client.
#   load: check JSON from the client and turn it into clean data for the models.
from marshmallow import Schema, ValidationError, fields, validate, validates


# A schema lists the fields for one kind of JSON object, plus the rules for each field.
class ExerciseSchema(Schema):
    # dump_only=True: the server sends the id, but the client cannot set it.
    id = fields.Int(dump_only=True)
    # validate.Length sets the shortest and longest allowed text.
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    equipment_needed = fields.Bool(required=True)

    # A length check would accept "   " (spaces only), so this extra check rejects it.
    # Raising ValidationError sends a 400 error back to the client.
    @validates('name')
    def validate_name_not_blank(self, value, **kwargs):
        if not value.strip():
            raise ValidationError('name must not be blank')

    @validates('category')
    def validate_category_not_blank(self, value, **kwargs):
        if not value.strip():
            raise ValidationError('category must not be blank')


# The schema for one workout entry (the reps, sets, and duration for one exercise).
class WorkoutExerciseSchema(Schema):
    # The three ids come from the URL, so the client never sends them in the body.
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    # validate.Range sets the smallest and largest allowed numbers.
    reps = fields.Int(required=True, validate=validate.Range(min=1, max=10000))
    sets = fields.Int(required=True, validate=validate.Range(min=1, max=100))
    duration_seconds = fields.Int(required=True, validate=validate.Range(min=1, max=86400))


# The schema for a workout. Its entries are nested inside it, so one response shows both.
class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1, max=1440))
    notes = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    # A list of entries. Each item uses WorkoutExerciseSchema. The client cannot set this list directly.
    workout_exercises = fields.List(
        fields.Nested(WorkoutExerciseSchema),
        dump_only=True,
    )
