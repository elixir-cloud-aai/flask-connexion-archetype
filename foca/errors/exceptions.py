"""Define and register exceptions raised in app context with Connexion app."""

from copy import deepcopy
import logging
from traceback import format_exception
from typing import (Dict, List)

import connexion
from connexion import FlaskApp
from connexion.lifecycle import ConnexionRequest, ConnexionResponse
from connexion.exceptions import (
    ExtraParameterProblem,
    Forbidden,
    OAuthProblem,
    Unauthorized,
)
from json import dumps
from werkzeug.exceptions import (
    BadRequest,
    BadGateway,
    GatewayTimeout,
    InternalServerError,
    NotFound,
    ServiceUnavailable,
)
import connexion.exceptions
import werkzeug.exceptions
import starlette.exceptions

from foca.models.config import _get_by_path, ExceptionConfig

# Get logger instance
logger = logging.getLogger(__name__)

# Default exceptions
exceptions = {
    Exception: {
        "title": "Internal Server Error",
        "status": 500,
    },
    BadRequest: {
        "title": "Bad Request",
        "status": 400,
    },
    ExtraParameterProblem: {
        "title": "Bad Request",
        "status": 400,
    },
    Unauthorized: {
        "title": "Unauthorized",
        "status": 401,
    },
    OAuthProblem: {
        "title": "Unauthorized",
        "status": 401,
    },
    Forbidden: {
        "title": "Forbidden",
        "status": 403,
    },
    NotFound: {
        "title": "Not Found",
        "status": 404,
    },
    InternalServerError: {
        "title": "Internal Server Error",
        "status": 500,
    },
    BadGateway: {
        "title": "Bad Gateway",
        "status": 502,
    },
    ServiceUnavailable: {
        "title": "Service Unavailable",
        "status": 502,
    },
    GatewayTimeout: {
        "title": "Gateway Timeout",
        "status": 504,
    }
}

exceptions_http = {
    400: {
        "title": "Bad Request",
        "status": 400,
    },
    401: {
        "title": "Unauthorized",
        "status": 401,
    },
    403: {
        "title": "Forbidden",
        "status": 403,
    },
    404: {
        "title": "Not Found",
        "status": 404,
    },
    500: {
        "title": "Internal Server Error",
        "status": 500,
    },
    502: {
        "title": "Bad Gateway",
        "status": 502,
    },
    504: {
        "title": "Gateway Timeout",
        "status": 504,
    }
}


def register_exception_handler(app: FlaskApp) -> FlaskApp:
    """Register generic JSON problem handler with Connexion application
    instance.

    Args:
        app: Connexion application instance.

    Returns:
        Connexion application instance with registered generic JSON problem
        handler.
    """
    app.add_error_handler(
        Exception,
        exception_handler_builtin,
    )
    app.add_error_handler(
        starlette.exceptions.HTTPException,
        exception_handler_starlette,
    )
    app.add_error_handler(
        connexion.exceptions.ProblemException,
        exception_handler_connexion,
    )
    logger.debug("Registered FOCA problem handler with Connexion app.")
    return app


def _exc_to_str(
    exc: BaseException,
    delimiter: str = "\\n",
) -> str:
    """Convert exception, including traceback, to string representation.

    Args:
        exc: The exception to convert to a string.
        delimiter: The delimiter used to join different lines of the exception
            stack.

    Returns:
        String representation of exception.
    """
    exc_lines = format_exception(
        exc.__class__,
        exc,
        exc.__traceback__
    )
    exc_stripped = [e.rstrip('\n') for e in exc_lines]
    exc_split = []
    for item in exc_stripped:
        exc_split.extend(item.splitlines())
    return delimiter.join(exc_split)


def _log_exception(
    exc: BaseException,
    format: str = 'oneline',
) -> None:
    """Log exception with indicated format.

    Requires a `logging` logger to be set up and configured.

    Args:
        exc: The exception to log.
        format: One of ``oneline`` (exception, including traceback logged to
            single line), ``minimal`` (log only exception title and message),
            or ``regular`` (exception logged with entire trace stack, typically
            across multiple lines).
    """
    exc_str = ''
    valid_formats = [
        'oneline',
        'minimal',
        'regular',
    ]
    if format in valid_formats:
        if format == "oneline":
            exc_str = _exc_to_str(exc=exc)
        elif format == "minimal":
            exc_str = f"{type(exc).__name__}: {str(exc)}"
        else:
            exc_str = _exc_to_str(
                exc=exc,
                delimiter='\n'
            )
        logger.error(exc_str)
    else:
        logger.error("Error logging is misconfigured.")


def _subset_nested_dict(
    obj: Dict,
    key_sequence: List,
) -> Dict:
    """Subset nested dictionary.

    Args:
        obj: (Nested) dictionary.
        key_sequence: Sequence of keys, to be applied from outside to inside,
            pointing to the key (and descendants) to keep.

    Returns:
        Subset of `obj`.
    """
    filt = {}
    if len(key_sequence):
        key = key_sequence.pop(0)
        filt[key] = obj[key]
        if len(key_sequence):
            filt[key] = _subset_nested_dict(filt[key], key_sequence)
    return filt


def _exclude_key_nested_dict(
    obj: Dict,
    key_sequence: List,
) -> Dict:
    """Exclude key from nested dictionary.

    Args:
        obj: (Nested) dictionary.
        key_sequence: Sequence of keys, to be applied from outside to inside,
            pointing to the key (and descendants) to delete.

    Returns:
        `obj` stripped of excluded key.
    """
    if len(key_sequence):
        key = key_sequence.pop(0)
        if len(key_sequence):
            _exclude_key_nested_dict(obj[key], key_sequence)
        else:
            del obj[key]
    return obj


def _problem_handler_json(
    request: ConnexionRequest,
    exception: Exception,
) -> ConnexionResponse:
    """Generic JSON problem handler.

    Args:
        exception: Raised exception.

    Returns:
        JSON-formatted error response.
    """
    logger.warning(f"Config: {connexion.request.state.config}")
    logger.warning(f"ExceptionConfig: {connexion.request.state.config.exceptions}")
    conf: ExceptionConfig = connexion.request.state.config.exceptions
    assert conf.mapping is not None
    exc = type(exception)
    logger.warning(f"Exception type: {exc}")
    logger.warning(f"Exception type dir: {dir(exc)}")
    logger.warning(f"Exception: {exception}")
    logger.warning(f"Exception dir: {dir(exception)}")
    logger.warning(f"Exception args: {exception.args}")
    logger.warning(f"Exception args dir: {dir(exception.args)}")
    logger.warning(f"Exception detail: {exception.detail}")
    logger.warning(f"Exception detail dir: {dir(exception.detail)}")
    logger.warning(f"Exception headers: {exception.headers}")
    logger.warning(f"Exception headers dir: {dir(exception.headers)}")
    logger.warning(f"Exception status code: {exception.status_code}")
    logger.warning(f"Exception status code dir: {dir(exception.status_code)}")
    if exc not in conf.mapping:
        exc = Exception
    try:
        status = int(_get_by_path(
            obj=conf.mapping[exc],
            key_sequence=conf.status_member,
        ))
    except KeyError:
        if conf.logging.value != "none":
            _log_exception(
                exc=exception,
                format=conf.logging.value
            )
        return ConnexionResponse(
            status_code=500,
            mimetype="application/problem+json",
        )
    # Log exception JSON & traceback
    if conf.logging.value != "none":
        logger.error(conf.mapping[exc])
        _log_exception(
            exc=exception,
            format=conf.logging.value
        )
    # Filter members to be returned to user
    keep = deepcopy(conf.mapping[exc])
    if conf.public_members is not None:
        keep = {}
        for member in deepcopy(conf.public_members):
            keep.update(_subset_nested_dict(
                obj=conf.mapping[exc],
                key_sequence=member,
            ))
    elif conf.private_members is not None:
        for member in deepcopy(conf.private_members):
            keep.update(_exclude_key_nested_dict(
                obj=keep,
                key_sequence=member,
            ))
    # Return response
    return ConnexionResponse(
        status_code=status,
        mimetype="application/problem+json",
        body=dumps(keep),
    )


def exception_handler_builtin(
    request: ConnexionRequest,
    exception: Exception,
) -> ConnexionResponse:
    """Return JSON-formatted error response for built-in exceptions.

    Return the ``500`` error response defined in the OpenAPI specification for
    the operation during which the exception was raised. If not defined, return
    the corresponding default response for that operation instead. If also not
    defined, or if the exception is not associated with a specific operation,
    return the defined global default response. If none of these are defined,
    return a generic RFC 9457-compliant error response.

    Args:
        request: Connexion request object.
        exception: Raised exception.

    Returns:
        JSON-formatted error response.
    """
    logger.warning(
        f'Exception "{exception}" of type "{type(exception)}" raised by '
        '"builtins.Exception" handler.'
    )
    return ConnexionResponse(
        status_code=500,
        mimetype="application/problem+json",
        body=dumps({"title": "Internal Server Error", "status": 500}),
    )


def exception_handler_connexion(
    request: ConnexionRequest,
    exception: Exception,
) -> ConnexionResponse:
    logger.warning(
        f'Exception "{exception}" of type "{type(exception)}" raised by '
        '"connexion.exceptions.ProblemException" handler.'
    )
    return ConnexionResponse(
        status_code=500,
        mimetype="application/problem+json",
        body=dumps({"title": "Internal Server Error", "status": 500}),
    )


def exception_handler_starlette(
    request: ConnexionRequest,
    exception: Exception,
) -> ConnexionResponse:
    logger.warning(
        f'Exception "{exception}" of type "{type(exception)}" raised by '
        '"starlette.exceptions.HTTPException" handler.'
    )
    return ConnexionResponse(
        status_code=500,
        mimetype="application/problem+json",
        body=dumps({"title": "Internal Server Error", "status": 500}),
    )
