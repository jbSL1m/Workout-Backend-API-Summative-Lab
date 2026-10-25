from marshmallow import Schema, ValidationError, fields, validate, validates


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    equipment_needed = fields.Bool(required=True)

    @validates('name')
    def validate_name_not_blank(self, value, **kwargs):
        if not value.strip():
            raise ValidationError('name must not be blank')

    @validates('category')
    def validate_category_not_blank(self, value, **kwargs):
        if not value.strip():
            raise ValidationError('category must not be blank')


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(required=True, validate=validate.Range(min=1, max=10000))
    sets = fields.Int(required=True, validate=validate.Range(min=1, max=100))
    duration_seconds = fields.Int(required=True, validate=validate.Range(min=1, max=86400))


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1, max=1440))
    notes = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    workout_exercises = fields.List(
        fields.Nested(WorkoutExerciseSchema),
        dump_only=True,
    )
