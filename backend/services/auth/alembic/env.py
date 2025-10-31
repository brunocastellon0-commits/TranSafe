import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import create_engine # <- MODIFICACIÓN: Importar create_engine

from alembic import context

# --- INICIO DE MODIFICACIÓN ---

# 1. Añadir la ruta raíz del microservicio (services/auth) al path
# Esto permite que env.py pueda importar 'app.config' y 'app.models'
# __file__ es .../auth/alembic/env.py
# os.path.dirname(__file__) es .../auth/alembic
# os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) es .../auth/
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

# 2. Importar tus settings y tu Base de modelos
from app.config import get_settings
# ¡¡IMPORTANTE!! Ajusta la siguiente línea para importar tu 'Base'
# Puede ser 'app.models.py', 'app.db.models', 'app.models.user', etc.
from app.database import Base # <- ¡¡AJUSTA ESTA LÍNEA!!
from app.models import user_model
settings = get_settings()

# --- FIN DE MODIFICACIÓN ---


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# --- MODIFICACIÓN ---
# Apuntar Alembic a la metadata de tus modelos
target_metadata = Base.metadata
# --- FIN DE MODIFICACIÓN ---


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    ...
    """
    
    # --- MODIFICACIÓN ---
    # Usar la DATABASE_URL de tus settings (.env)
    # url = config.get_main_option("sqlalchemy.url") # Línea original
    url = settings.DATABASE_URL
    # --- FIN DE MODIFICACIÓN ---

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    ...
    """
    
    # --- MODIFICACIÓN ---
    # Establecer la URL de la base de datos desde tus settings (.env)
    # Esto sobreescribe la URL de 'alembic.ini'
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    
    # El resto del código usará esta URL que acabamos de setear
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    # --- FIN DE MODIFICACIÓN ---

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()