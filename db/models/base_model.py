from datetime import datetime
from typing import Annotated

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.sql import func

intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
str_300 = Annotated[str, 300]
datetime_auto = Annotated[datetime, mapped_column(default=func.now())]


class Base(DeclarativeBase):
    type_annotation_map = {
        intpk: Integer,
        str_300: String(300),
        datetime_auto: DateTime,
    }
