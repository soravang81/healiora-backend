import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Add your app to sys.path so Alembic can find modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import settings and models
from app.core.config import settings
from app.db.session import Base
from app.db.models import patient, credential, medical_records, hospital, doctor, ambulance, socket_log, patient_assignment

# Alembic Config object
config = context.config

# Setup Python logging based on .ini config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Provide metadata for Alembic's 'autogenerate' support
target_metadata = Base.metadata

# Set database URL from FastAPI settings
def get_url():
    return settings.DATABASE_URL

config.set_main_option("sqlalchemy.url", get_url())

def run_migrations_offline():
    """Run migrations without connecting to the database (e.g., for generating SQL files)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations with a database connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
