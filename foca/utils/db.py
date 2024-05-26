"""Utility functions for interacting with a MongoDB database collection."""

from typing import (Any, Mapping, Optional)

from bson.objectid import ObjectId
from pymongo.collection import Collection

from foca.models.config import Config


def find_one_latest(collection: Collection) -> Optional[Mapping[Any, Any]]:
    """Return newest document, stripped of `ObjectId`.

    Args:
        collection: MongoDB collection from which the document is to be
            retrieved.

    Returns:
        Newest document or ``None``, if no document exists.
    """
    try:
        return collection.find(
            {},
            {'_id': False}
        ).sort([('_id', -1)]).limit(1).next()
    except StopIteration:
        return None


def find_id_latest(collection: Collection) -> Optional[ObjectId]:
    """Return `ObjectId` of newest document.

    Args:
        collection: MongoDB collection from which `ObjectId` is to be
            retrieved.

    Returns:
        `ObjectId` of newest document or ``None``, if no document exists.
    """
    try:
        return collection.find().sort([('_id', -1)]).limit(1).next()['_id']
    except StopIteration:
        return None


def get_client(config: Config, db: str, collection: str) -> Collection:
    """Get client for a given database collection.

    Args:
        config: Application configuration.

    Raises:
        AssertionError: If the database configuration is invalid or incomplete,
            or the specified database or collection is missing.
    """
    assert config.db is not None, "Database configuration is missing."
    assert config.db.dbs is not None, "Database connections are missing."

    my_db = config.db.dbs.get(db)
    assert my_db is not None, f"Database '{db}' is missing."
    assert my_db.collections is not None, f"Database '{db}' has no collections."

    my_collection = my_db.collections.get(collection)
    assert my_collection is not None, (
        f"Database collection '{collection}' is missing."
    )
    assert my_collection.client is not None, (
        f"Database collection '{collection}' is missing."
    )

    return my_collection.client
