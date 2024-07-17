"""Init of DB

Revision ID: 23d96199e2e5
Revises: 
Create Date: 2024-07-17 13:28:22.093582

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "23d96199e2e5"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "skins",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("skin_name", sa.String(length=300), nullable=False),
        sa.Column("float", sa.String(length=300), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("skins")
    # ### end Alembic commands ###
