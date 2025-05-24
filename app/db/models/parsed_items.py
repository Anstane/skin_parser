from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ParsedItems(Base):
    __tablename__ = "parsed_items"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        unique=True,
    )
    tg_id: Mapped[int]
    skin_name: Mapped[str]
    pattern: Mapped[int | None]
    item_float: Mapped[str | None]
    price: Mapped[float | None]
    lis_item_id: Mapped[int]
    created_at_lis: Mapped[str | None]
    unlock_at_lis: Mapped[str | None]
    event: Mapped[str]
