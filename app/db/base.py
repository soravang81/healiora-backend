from app.db.base_class import Base  # ✅ import base class for all models
from app.db.models.user_model import User  # ✅ import all models here so Alembic sees them