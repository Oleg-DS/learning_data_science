# -*- coding: utf-8 -*-

from enum import Enum

token = '' # Вставить сюда токен бота
db_file = "database.vdb"


class States(Enum):
    """
    Мы используем БД Vedis, в которой хранимые значения всегда строки,
    поэтому и тут будем использовать тоже строки (str)
    """
    S_START = "10"  # Начало нового диалога
    S_COUNTRY = "11"
    S_TOP = "21"
    S_COUNTRY_YEAR = "12"
    S_TOP_YEAR = "22"
    S_COUNTRY_NAME = "13"
