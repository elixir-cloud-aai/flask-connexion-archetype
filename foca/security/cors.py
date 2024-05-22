"""Resources for cross-origin resource sharing (CORS)."""

import logging

from connexion import FlaskApp
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

# Get logger instance
logger = logging.getLogger(__name__)


def enable_cors(app: FlaskApp) -> FlaskApp:
    """Enables cross-origin resource sharing (CORS).

    Args:
        app: Connexion application instance.
    """
    app.add_middleware(
        CORSMiddleware,  # type: ignore
        position=MiddlewarePosition.BEFORE_EXCEPTION,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.debug('Enabled CORS for Connexion app.')
    return app
