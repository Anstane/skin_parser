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
    price: Mapped[str | None]
    ready_to_buy: Mapped[bool] = mapped_column(default=False)
