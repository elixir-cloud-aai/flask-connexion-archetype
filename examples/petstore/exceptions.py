"""Petstore exceptions."""

from connexion.exceptions import BadRequestProblem, ProblemException
from starlette.exceptions import HTTPException
from werkzeug.exceptions import (
    InternalServerError,
    NotFound,
)
import connexion.exceptions
import starlette.exceptions
import werkzeug.exceptions


class WrappedException(KeyError):
    """Raised when task with given task identifier was not found."""


class WrappedExceptionConnexion(connexion.exceptions.BadRequestProblem):
    """Raised when task with given task identifier was not found."""


class WrappedExceptionStarlette(starlette.exceptions.HTTPException):
    """Raised when task with given task identifier was not found."""


class WrappedExceptionWerkzeug(werkzeug.exceptions.NotFound):
    """Raised when task with given task identifier was not found."""


class CustomException(Exception):
    def __init__(
        self,
        message: str = "Custom exception",
    ):
        super().__init__(message)


class CustomExceptionConnexion(ProblemException):
    def __init__(
        self,
        status: int = 403,
        title: str = "CustomExceptionConnexion",
        detail: str = "Custom exception Connexion",
    ):
        super().__init__(status=status, title=title, detail=detail)


class CustomExceptionStarlette(HTTPException):
    def __init__(
        self,
        status_code: int = 403,
        detail: str = "Custom exception Starlette",
    ):
        super().__init__(status_code, detail)


class CustomExceptionWerkzeug(werkzeug.exceptions.HTTPException):
    def __init__(
        self,
        description: str = "Custom exception Werkzeug",
        response=None,
    ):
        super().__init__(description=description, response=response)

    code = 400


exceptions = {
    Exception: {
        "message": "Oops, something unexpected happened.",
        "code": 500,
    },
    BadRequestProblem: {
        "message": "We don't quite understand what it is you are looking for.",
        "code": 400,
    },
    NotFound: {
        "message": "We have never heard of this pet! :-(",
        "code": 404,
    },
    InternalServerError: {
        "message": "We seem to be having a problem here in the petstore.",
        "code": 500,
    },
}
