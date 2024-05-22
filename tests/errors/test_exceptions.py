"""
Tests for exceptions.py
"""

from copy import deepcopy
import json

from connexion import FlaskApp
from connexion.lifecycle import ConnexionResponse
import pytest


from foca.errors.exceptions import (
    _exc_to_str,
    _exclude_key_nested_dict,
    _problem_handler_json,
    _log_exception,
    register_exception_handler,
    _subset_nested_dict,
)
from foca.models.config import Config

EXCEPTION_INSTANCE = Exception()
INVALID_LOG_FORMAT = 'unknown_log_format'
TEST_DICT = {
    "title": "MyException",
    "details": {
        "code": 400,
        "description": "Some exception",
    },
    "status": 400,
}
TEST_KEYS = ['details', 'code']
EXPECTED_SUBSET_RESULT = {
    "details": {
        "code": 400,
    },
}
EXPECTED_EXCLUDE_RESULT = {
    "title": "MyException",
    "details": {
        "description": "Some exception",
    },
    "status": 400,
}
PUBLIC_MEMBERS = [['title']]
PRIVATE_MEMBERS = [['status']]


class UnknownException(Exception):
    pass


@pytest.fixture
def foca_app():
    """Create a Connexion app."""
    app = FlaskApp(__name__)
    setattr(app.app.config, 'foca', Config())
    return app


@pytest.fixture
def mock_connexion_request(mocker):
    request = mocker.MagicMock()
    request.headers = {}
    request.args = {}
    request.json = {}
    request.method = "GET"
    request.path = "/test_endpoint"
    return request


def test_register_exception_handler():
    """Test exception handler registration with Connexion app."""
    app = FlaskApp(__name__)
    ret = register_exception_handler(app)
    assert isinstance(ret, FlaskApp)


def test__exc_to_str():
    """Test exception reformatter function."""
    res = _exc_to_str(exc=EXCEPTION_INSTANCE)
    assert isinstance(res, str)


@pytest.mark.parametrize("format", ['oneline', 'minimal', 'regular'])
def test__log_exception(caplog, format):
    """Test exception reformatter function."""
    _log_exception(
        exc=EXCEPTION_INSTANCE,
        format=format,
    )
    assert "Exception" in caplog.text


def test__log_exception_invalid_format(caplog):
    """Test exception reformatter function with invalid format argument."""
    _log_exception(
        exc=EXCEPTION_INSTANCE,
        format=INVALID_LOG_FORMAT,
    )
    assert "logging is misconfigured" in caplog.text


def test__subset_nested_dict():
    """Test nested dictionary subsetting function."""
    res = _subset_nested_dict(
        obj=TEST_DICT,
        key_sequence=deepcopy(TEST_KEYS)
    )
    assert res == EXPECTED_SUBSET_RESULT


def test__exclude_key_nested_dict():
    """Test function to exclude a key from a nested dictionary."""
    res = _exclude_key_nested_dict(
        obj=TEST_DICT,
        key_sequence=deepcopy(TEST_KEYS)
    )
    assert res == EXPECTED_EXCLUDE_RESULT


def test__problem_handler_json(foca_app, mock_connexion_request):
    """Test problem handler with instance of custom, unlisted error."""
    EXPECTED_RESPONSE = (
        foca_app.app.config.foca.exceptions.mapping[Exception]  # type: ignore
    )
    with foca_app.app.app_context():
        res = _problem_handler_json(mock_connexion_request, UnknownException())
        assert isinstance(res, ConnexionResponse)
        assert res.status_code == 500
        assert res.mimetype == "application/problem+json"
        response = json.loads(res.body)  # type: ignore
        assert response == EXPECTED_RESPONSE


def test__problem_handler_json_no_fallback_exception(
    foca_app,
    mock_connexion_request
):
    """Test problem handler; unlisted error without fallback."""
    del foca_app.app.config.foca.exceptions.mapping[Exception]  # type: ignore
    with foca_app.app.app_context():
        res = _problem_handler_json(mock_connexion_request, UnknownException())
        assert isinstance(res, ConnexionResponse)
        assert res.status_code == 500
        assert res.mimetype == "application/problem+json"
        response = res.body
        assert response is None


def test__problem_handler_json_with_public_members(
    foca_app,
    mock_connexion_request
):
    """Test problem handler with public members."""
    foca_app.app.config.foca.exceptions.public_members = (  # type: ignore
        PUBLIC_MEMBERS
    )
    with foca_app.app.app_context():
        res = _problem_handler_json(mock_connexion_request, UnknownException())
        assert isinstance(res, ConnexionResponse)
        assert res.status_code == 500
        assert res.mimetype == "application/problem+json"


def test__problem_handler_json_with_private_members(
    foca_app,
    mock_connexion_request
):
    """Test problem handler with private members."""
    foca_app.app.config.foca.exceptions.private_members = (  # type: ignore
        PRIVATE_MEMBERS
    )
    with foca_app.app.app_context():
        res = _problem_handler_json(mock_connexion_request, UnknownException())
        assert isinstance(res, ConnexionResponse)
        assert res.status_code == 500
        assert res.mimetype == "application/problem+json"
