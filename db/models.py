from datetime import datetime

from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()


class Skins(Base):
    """Table for storing best value of skins."""

    __tablename__ = "skins"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    skin_name: Mapped[str] = mapped_column(String(300))
    float_value: Mapped[str] = mapped_column(String(10))
    timestamp: Mapped[datetime] = mapped_column(default=func.now())
