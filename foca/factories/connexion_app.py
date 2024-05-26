"""Factory for creating and configuring Connexion application instances."""

import contextlib
from inspect import stack
import logging
from typing import AsyncIterator, Optional

from connexion import FlaskApp, ConnexionMiddleware

from foca.models.config import Config

# Get logger instance
logger = logging.getLogger(__name__)


def create_connexion_app(config: Optional[Config] = Config()) -> FlaskApp:
    """Create and configure Connexion application instance.

    Args:
        config: Application configuration.

    Returns:
        Connexion application instance.
    """

    @contextlib.asynccontextmanager
    async def config_handler(app: ConnexionMiddleware) -> AsyncIterator:
        yield {"config": config}

    # Instantiate Connexion app
    app = FlaskApp(
        __name__,
        lifespan=config_handler,
    )

    calling_module = ':'.join([stack()[1].filename, stack()[1].function])
    logger.debug(f"Connexion app created from '{calling_module}'.")

    return app
