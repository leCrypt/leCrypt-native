import pytest

import flask


@pytest.fixture
def client():
    flask.app.config['TESTING'] = True

    with flask.app.test_client() as client:
        yield client


