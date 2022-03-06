"""Methods to manage permission management configuration"""

import logging
from connexion import App
from flask_authz import CasbinEnforcer
from pkg_resources import resource_filename

from foca.models.config import (
    DBConfig,
    MongoConfig,
    SpecConfig,
    CollectionConfig,
    AccessControlConfig
)
from foca.database.register_mongodb import add_new_database
from foca.access_control.foca_casbin_adapter.adapter import Adapter
from foca.access_control.constants import ACCESS_CONTROL_BASE_PATH

logger = logging.getLogger(__name__)


def register_access_control(
    cnx_app: App,
    mongo_config: MongoConfig,
    access_control_config: AccessControlConfig
) -> App:
    """Register access control configuration with flask app.

    Args:
        cnx_app: Connexion application instance.
        mongo_config: :py:class:`foca.models.config.AccessControlConfig`
            instance describing databases and collections to be registered
            with `app`.
        access_control_config: :py:class:
            `foca.models.config.AccessControlConfig` instance describing
            access control to be registered with `app`.

    Returns:
        Connexion application instance with registered access control config.
    """
    # Register access control database and collection.
    access_db_conf = DBConfig(
        collections={
            access_control_config.collection_name: CollectionConfig()
        },
        client=None
    )

    # Set default db attributes if config not present.
    if mongo_config is None:
        mongo_config = MongoConfig()

    if mongo_config.dbs is None:
        mongo_config.dbs = {access_control_config.db_name: access_db_conf}
    else:
        mongo_config.dbs[access_control_config.db_name] = access_db_conf

    cnx_app.app.config['FOCA'].db = mongo_config

    # Register new database for access control.
    add_new_database(
        app=cnx_app.app,
        conf=mongo_config,
        db_conf=access_db_conf,
        db_name=access_control_config.db_name
    )

    # Register access control api specs and corresponding controller.
    cnx_app = register_permission_specs(
        app=cnx_app,
        access_control_config=access_control_config
    )
    cnx_app = register_casbin_enforcer(
        app=cnx_app,
        mongo_config=mongo_config,
        access_control_config=access_control_config
    )

    return cnx_app


def register_permission_specs(
    app: App,
    access_control_config: AccessControlConfig
):
    """Register open api specs for permission management.

    Args:
        app: Connexion application instance.
        access_control_config: :py:class:
            `foca.models.config.AccessControlConfig` instance describing
            access control to be registered with `app`.

    Returns:
        Connexion app with updated permission specifications.
    """
    # Check if default, get package path variables for specs.
    if access_control_config.use_default_api_specs:
        spec_path = str(resource_filename(
            ACCESS_CONTROL_BASE_PATH, access_control_config.api_specs_path
        ))
    else:
        spec_path = access_control_config.api_specs_path

    spec = SpecConfig(
        path=spec_path,
        add_operation_fields={
            "x-openapi-router-controller": (
                access_control_config.api_spec_controller_path
            )
        },
        connexion={
            "strict_validation": True,
            "validate_responses": False,
            "options": {
                "swagger_ui": True,
                "serve_spec": True
            }
        }
    )

    app.add_api(
        specification=spec.path[0],
        **spec.dict().get('connexion', {}),
    )
    return app


def register_casbin_enforcer(
    app: App,
    access_control_config: AccessControlConfig,
    mongo_config: MongoConfig
) -> App:
    """Method to add casbin permission enforcer.

    Args:
        app: Connexion app.
        access_control_config: :py:class:
            `foca.models.config.AccessControlConfig` instance describing
            access control to be registered with `app`.
        mongo_config: :py:class:`foca.models.config.MongoConfig` instance
            describing databases and collections to be registered with `app`.

    Returns:
        Connexion application instance with registered casbin configuration.
    """
    # Check if default, get package path variables for policies.
    if access_control_config.use_default_api_specs:
        policy_path = str(resource_filename(
            ACCESS_CONTROL_BASE_PATH, access_control_config.policy_path
        ))
    else:
        policy_path = access_control_config.policy_path

    logger.info("Setting casbin policies.")
    app.app.config['CASBIN_MODEL'] = policy_path

    logger.info("Setting headers for owner operations.")
    app.app.config['CASBIN_OWNER_HEADERS'] = (
        access_control_config.owner_headers
    )

    logger.info("Setting headers for user operations.")
    app.app.config['CASBIN_USER_NAME_HEADERS'] = (
        access_control_config.user_headers
    )

    logger.info("Setting up casbin enforcer.")
    adapter = Adapter(
        uri=f"mongodb://{mongo_config.host}:{mongo_config.port}/",
        dbname=access_control_config.db_name,
        collection=access_control_config.collection_name
    )
    casbin_enforcer = CasbinEnforcer(app.app, adapter)

    app.app.config['casbin_enforcer'] = casbin_enforcer
    app.app.config['casbin_adapter'] = adapter

    return app