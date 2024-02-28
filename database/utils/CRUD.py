from typing import Dict, List, TypeVar

from peewee import ModelSelect

from database.common.models import ModelBase
from ..common.models import db

T = TypeVar("T")


def _store_date(db: db, model: T, *data: List[Dict]) -> None:
    """
    Stores data to db
    :param db: database
    :param model: used model (for example History)
    :param data: data to store
    :return:
    """
    with db.atomic():
        model.insert_many(*data).execute()


def _retrieve_all_data(db: db, model: T, *columns: ModelBase) -> ModelSelect:
    """
    Gives columns from db
    :param db: database
    :param model: used model (for example History)
    :param columns: columns to retrive
    :return:
    """
    with db.atomic():
        response = model.select(*columns)

    return response


class CRUDInteface():
    @staticmethod
    def create():
        return _store_date

    @staticmethod
    def retrieve():
        return _retrieve_all_data


if __name__ == "__main__":
    _store_date()
    _retrieve_all_data()
    CRUDInteface()
