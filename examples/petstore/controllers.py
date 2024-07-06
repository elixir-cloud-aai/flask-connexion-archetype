"""Petstore controllers."""

import logging

from connexion import request
from flask import make_response
from foca.utils.db import get_client
from foca.utils.logging import log_traffic
from foca.models.config import Config

from exceptions import (
    NotFound,
    CustomException,
    CustomExceptionStarlette,
    CustomExceptionWerkzeug,
    CustomExceptionConnexion,
    WrappedException,
    WrappedExceptionConnexion,
    WrappedExceptionStarlette,
    WrappedExceptionWerkzeug,
)
import connexion.exceptions
import starlette.exceptions
import werkzeug.exceptions

logger = logging.getLogger(__name__)


@log_traffic
def findPets(limit=None, tags=None):
    config: Config = request.state.config
    logger.warning(f"Config: {config}")
    client = get_client(config=config, db='petstore', collection='pets')
    filter_dict = {} if tags is None else {'tag': {'$in': tags}}
    if not limit:
        limit = 0
    records = client.find(
        filter_dict,
        {'_id': False}
    ).sort([('$natural', -1)]).limit(limit)
    return list(records)


@log_traffic
def addPet(pet):
    config: Config = request.state.config
    client = get_client(config=config, db='petstore', collection='pets')
    counter = 0
    ctr = client.find({}).sort([('$natural', -1)])
    if not client.count_documents({}) == 0:
        counter = ctr[0].get('id') + 1
    record = {
        "id": counter,
        "name": pet['name'],
        "tag": pet['tag']
    }
    client.insert_one(record)
    del record['_id']
    return record


@log_traffic
def findPetById(id):
    config: Config = request.state.config
    client = get_client(config=config, db='petstore', collection='pets')
    record = client.find_one(
        {"id": id},
        {'_id': False},
    )
    if record is None:
        raise NotFound
    return record


@log_traffic
def deletePet(id):
    config: Config = request.state.config
    client = get_client(config=config, db='petstore', collection='pets')
    record = client.find_one(
        {"id": id},
        {'_id': False},
    )
    if record is None:
        raise NotFound
    client.delete_one(
        {"id": id},
    )
    response = make_response('', 204)
    return response


@log_traffic
def exceptionWrapped():
    raise WrappedException


@log_traffic
def exceptionWrappedConnexion():
    raise WrappedExceptionConnexion


@log_traffic
def exceptionWrappedStarlette():
    raise WrappedExceptionStarlette(
        status_code=404,
        detail="Wrapper exception Starlette."
    )


@log_traffic
def exceptionWrappedWerkzeug():
    raise WrappedExceptionWerkzeug


@log_traffic
def exceptionCustom():
    raise CustomException


@log_traffic
def exceptionCustomConnexion():
    raise CustomExceptionConnexion


@log_traffic
def exceptionCustomStarlette():
    raise CustomExceptionStarlette


@log_traffic
def exceptionCustomWerkzeug():
    raise CustomExceptionWerkzeug


@log_traffic
def exceptionBuiltin():
    raise TypeError


@log_traffic
def exceptionBuiltinConnexion():
    raise connexion.exceptions.Unauthorized


@log_traffic
def exceptionBuiltinStarlette():
    raise starlette.exceptions.HTTPException(
        status_code=404,
        detail="Builtin exception Starlette."
    )


@log_traffic
def exceptionBuiltinWerkzeug():
    raise werkzeug.exceptions.Forbidden
