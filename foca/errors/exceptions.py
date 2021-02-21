"""Define and register exceptions raised in app context with Connexion app."""

from copy import deepcopy
import logging
from traceback import format_exception
from typing import (Dict, List)

from connexion import App
from connexion.exceptions import (
    ExtraParameterProblem,
    Forbidden,
    OAuthProblem,
    Unauthorized,
)
from flask import (current_app, Response)
from json import dumps
from werkzeug.exceptions import (
    BadRequest,
    BadGateway,
    GatewayTimeout,
    InternalServerError,
    NotFound,
    ServiceUnavailable,
)

from foca.models.config import get_by_path

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


def register_exception_handler(app: App) -> App:
    """Register generic JSON problem handler with Connexion app.

    Args:
        app (App): Connexion app.

    Returns:
        App: Connexion app with registered generic JSON problem handler.
    """
    app.add_error_handler(Exception, handle_problem)
    logger.debug("Registered generic JSON problem handler with Connexion app.")
    return app


def exc_to_str(
    exc: BaseException,
    delimiter: str = "\\n",
) -> str:
    """Convert exception, including traceback, to string representation.

    Args:
        exc (BaseException): The exception to convert to a string.
        delimiter (str, optional): The delimiter used to join different lines
            of the exception stack. Defaults to "\\n".

    Returns:
        str: String representation of exception. 
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


def log_exception(
    exc: BaseException,
    format: str = 'oneline',
) -> None:
    """Log exception with indicated format.

    Note:
        Requires a `logging` logger to be set up and configured.

    Args:
        exc (BaseException): The exception to log.
        format (str, optional): One of 'oneline' (default), 'minimal', or
            'regular'. Defaults to 'oneline'. ``oneline``: Exception,
            including traceback, is logged on a single line. ``minimal``:
            Only the exception title and message are logged. ``regular``:
            The exception is logged with the entire traceback stack, usually
            on multiple lines.
    """
    exc_str = ''
    valid_formats = [
        'oneline',
        'minimal',
        'regular',
    ]
    if format in valid_formats:
        if format == "oneline":
            exc_str = exc_to_str(exc=exc)
        elif format == "minimal":
            exc_str = f"{type(exc).__name__}: {str(exc)}"
        else:
            exc_str = exc_to_str(
                exc=exc,
                delimiter='\n'
            )
        logger.error(exc_str)
    else:
        logger.error("Error logging is misconfigured.")


def subset_nested_dict(
    obj: Dict,
    key_sequence: List,
) -> Dict:
    """Create subset of nested dictionary.

    Args:
        obj (Dict): A (nested) dictionary.
        key_sequence (List): A sequence of keys, to be applied from outside to
            inside, pointing to the key (and descendants) to keep.

    Returns:
        Dict: Subset of input dictionary.
    """
    filt = {}
    if len(key_sequence):
        key = key_sequence.pop(0)
        filt[key] = obj[key]
        if len(key_sequence):
            filt[key] = subset_nested_dict(filt[key], key_sequence)
    return filt


def exclude_key_nested_dict(
    obj: Dict,
    key_sequence: List,
) -> Dict:
    """Exclude key from nested dictionary.

    Args:
        obj (Dict): A (nested) dictionary.
        key_sequence (List): A sequence of keys, to be applied from outside to
            inside, pointing to the key (and descendants) to delete.

    Returns:
        Dict: Dictionary minus the excluded key.
    """
    if len(key_sequence):
        key = key_sequence.pop(0)
        if len(key_sequence):
            exclude_key_nested_dict(obj[key], key_sequence)
        else:
            del obj[key]
    return obj


def handle_problem(exception: Exception) -> Response:
    """Generic JSON problem handler.

    Args:
        exception (Exception): The raised exception.

    Returns:
        Response: JSON-formatted error response.
    """
    # Look up exception & get status code
    conf = current_app.config['FOCA'].exceptions
    exc = type(exception)
    if exc not in conf.mapping:
        exc = Exception
    try:
        status = int(get_by_path(
            obj=conf.mapping[exc],
            key_sequence=conf.status_member,
        ))
    except KeyError:
        if conf.logging.value != "none":
            log_exception(
                exc=exception,
                format=conf.logging.value
            )
        return Response(
            status=500,
            mimetype="application/problem+json",
        )
    # Log exception JSON & traceback
    if conf.logging.value != "none":
        logger.error(conf.mapping[exc])
        log_exception(
            exc=exception,
            format=conf.logging.value
        )
    # Filter members to be returned to user
    keep = deepcopy(conf.mapping[exc])
    if conf.public_members is not None:
        keep = {}
        for member in deepcopy(conf.public_members):
            keep.update(subset_nested_dict(
                obj=conf.mapping[exc],
                key_sequence=member,
            ))
    elif conf.private_members is not None:
        for member in deepcopy(conf.private_members):
            keep.update(exclude_key_nested_dict(
                obj=keep,
                key_sequence=member,
            ))
    # Return response
    return Response(
        response=dumps(keep),
        status=status,
        mimetype="application/problem+json",
    )
