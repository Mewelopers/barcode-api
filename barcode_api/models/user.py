import sqlalchemy as sa
from barcode_api.config.database import Base


class User(Base):
    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.String(255), unique=True, index=True, nullable=False)
    password = sa.Column(sa.String(255), nullable=False)
    is_active = sa.Column(sa.Boolean(), default=True)
    last_updated = sa.Column(
        sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()
    )
