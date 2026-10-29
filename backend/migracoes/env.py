from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from configuracao import obter_configuracao


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline():
    url = obter_configuracao().url_do_banco
    if not url:
        raise RuntimeError("Configure DATABASE_URL com a URL PostgreSQL do Supabase.")
    context.configure(
        url=url,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    url = obter_configuracao().url_do_banco
    if not url:
        raise RuntimeError("Configure DATABASE_URL com a URL PostgreSQL do Supabase.")
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
