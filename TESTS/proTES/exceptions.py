"""proTES exceptions."""

from connexion.exceptions import (  # type: ignore
    BadRequestProblem,
    ExtraParameterProblem,
    Forbidden,
    Unauthorized,
)
from pydantic import ValidationError
from pymongo.errors import PyMongoError  # type: ignore
from werkzeug.exceptions import (
    BadRequest,
    InternalServerError,
    NotFound,
)

# pylint: disable="too-few-public-methods"


class TaskNotFound(NotFound):
    """Raised when task with given task identifier was not found."""


class IdsUnavailableProblem(PyMongoError):
    """Raised when task identifier is unavailable."""


class NoTesInstancesAvailable(ValueError):
    """Raised when no TES instances are available."""


class MiddlewareException(ValueError):
    """Raised when a middleware could not be applied."""


class InvalidMiddleware(MiddlewareException):
    """Raised when a middleware is invalid."""


exceptions = {
    Exception: {
        "message": "An unexpected error occurred.",
        "code": "500",
    },
    BadRequest: {
        "message": "The request is malformed.",
        "code": "400",
    },
    BadRequestProblem: {
        "message": "The request is malformed.",
        "code": "400",
    },
    ExtraParameterProblem: {
        "message": "The request is malformed.",
        "code": "400",
    },
    ValidationError: {
        "message": "The request is malformed.",
        "code": "400",
    },
    Unauthorized: {
        "message": " The request is unauthorized.",
        "code": "401",
    },
    Forbidden: {
        "message": "The requester is not authorized to perform this action.",
        "code": "403",
    },
    NotFound: {
        "message": "The requested resource wasn't found.",
        "code": "404",
    },
    TaskNotFound: {
        "message": "The requested task wasn't found.",
        "code": "404",
    },
    InternalServerError: {
        "message": "An unexpected error occurred.",
        "code": "500",
    },
    IdsUnavailableProblem: {
        "message": "No/few unique task identifiers available.",
        "code": "500",
    },
    NoTesInstancesAvailable: {
        "message": "No valid TES instances available.",
        "code": "500",
    },
    MiddlewareException: {
        "message": "Middleware could not be applied.",
        "code": "500",
    },
    InvalidMiddleware: {
        "message": "Middleware is invalid.",
        "code": "500",
    },
}
