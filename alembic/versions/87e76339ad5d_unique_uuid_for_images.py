"""unique uuid for images

Revision ID: 87e76339ad5d
Revises: 10570f725f26
Create Date: 2023-06-07 20:36:32.795341

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "87e76339ad5d"
down_revision = "10570f725f26"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint("ImageData_unique_id", "ImageData", ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("ImageData_unique_id", "ImageData", type_="unique")
    # ### end Alembic commands ###