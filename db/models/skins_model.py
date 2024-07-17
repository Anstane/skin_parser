from sqlalchemy.orm import Mapped

from .base_model import Base, datetime_auto, intpk, str_300


class Skins(Base):
    """Table for storage best value of skins."""

    __tablename__ = "skins"

    id: Mapped[intpk]
    skin_name: Mapped[str_300]
    float: Mapped[str_300]
    timestamp: Mapped[datetime_auto]
