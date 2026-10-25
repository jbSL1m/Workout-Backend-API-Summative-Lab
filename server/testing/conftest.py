import os

# Must be set before app.py is imported so the app binds to the in-memory test database.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# conftest.py is a special pytest file. Its fixtures are shared by every test file in this folder.
import pytest  # noqa: E402

from app import app as flask_app  # noqa: E402
from models import db  # noqa: E402


# A fixture is setup code that a test asks for by naming it in its arguments.
@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    with flask_app.app_context():
        # Create empty tables before each test.
        db.create_all()
        # yield pauses here and hands the app to the test. The code after yield runs when the test ends.
        yield flask_app
        # Clean up: remove the session and drop the tables, so the next test starts empty.
        db.session.remove()
        db.drop_all()


# client depends on app, so pytest runs app first. It returns a fake browser that can call routes.
@pytest.fixture
def client(app):
    return app.test_client()
