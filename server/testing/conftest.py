import os

# Must be set before app.py is imported so the app binds to the in-memory test database.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest  # noqa: E402

from app import app as flask_app  # noqa: E402
from models import db  # noqa: E402


@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
