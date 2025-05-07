from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class SkinToParse(Base):
    __tablename__ = "skin_to_parse"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        unique=True,
    )
    tg_id: Mapped[int]
    skin_name: Mapped[str]
    patterns: Mapped[str | None]
    float: Mapped[str | None]

    # __table_args__ = (UniqueConstraint("tg_id", "skin_name", name="uix_tg_skin_name"),)
