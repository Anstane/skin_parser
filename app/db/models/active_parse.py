from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ActiveParse(Base):
    __tablename__ = "active_parses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        unique=True,
    )
    tg_id: Mapped[int] = mapped_column(
        unique=True,
    )
    is_active: Mapped[bool] = mapped_column(default=False)
