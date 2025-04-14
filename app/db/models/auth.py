from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class AuthLis(Base):
    __tablename__ = "auth_lis"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        unique=True,
    )
    tg_id: Mapped[int] = mapped_column(
        unique=True,
    )
    lis_token: Mapped[str]
