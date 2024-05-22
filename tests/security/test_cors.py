"""Unit test for security.cors.py"""

import functools

from connexion import FlaskApp
from starlette.middleware.cors import CORSMiddleware

from foca.security.cors import enable_cors


def test_enable_cors():
    """Test that CORS is called with app as a parameter."""
    app = FlaskApp(__name__)
    expected_middleware = functools.partial(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    assert not any(
        isinstance(item, functools.partial)
        and item.func == expected_middleware.func
        and item.args == expected_middleware.args
        for item in app.middleware.middlewares
    )
    enable_cors(app)
    assert any(
        isinstance(item, functools.partial)
        and item.func == expected_middleware.func
        and item.args == expected_middleware.args
        for item in app.middleware.middlewares
    )
