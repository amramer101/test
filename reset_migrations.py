#!/usr/bin/env python3
"""
reset_migrations.py

A management script to reset Django migration history and database state.
- Clears the django_migrations table
- Deletes all migration files (except __init__.py) from all apps
- Optionally drops and recreates the database (with confirmation)
- Logs all operations for debugging and safety

Usage:
    python reset_migrations.py [--drop-db] [--noinput]

Options:
    --drop-db   Drop and recreate the database (DANGEROUS: all data will be lost)
    --noinput   Do not prompt for confirmation (use with caution)
"""

import os
import sys
import shutil
import logging
import psycopg2
from pathlib import Path

# --- CONFIGURATION ---

# Update these as needed for your project
PROJECT_ROOT = Path(__file__).parent
APPS_DIR = PROJECT_ROOT / "apps"
DJANGO_MIGRATIONS_TABLE = "django_migrations"

# Database config (read from environment or hardcode for dev)
DB_NAME = os.environ.get("DB_NAME", "rm_platform_dev")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def confirm(prompt):
    try:
        return input(prompt).strip().lower() in ("y", "yes")
    except EOFError:
        return False


def clear_migration_files(app_path):
    migrations_path = app_path / "migrations"
    if not migrations_path.exists():
        return
    for file in migrations_path.iterdir():
        if file.is_file() and file.name != "__init__.py":
            logging.info(f"Deleting migration file: {file}")
            file.unlink()
    # Ensure __init__.py exists
    init_file = migrations_path / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        logging.info(f"Created: {init_file}")


def clear_all_migrations(apps_dir):
    for app in apps_dir.iterdir():
        if app.is_dir() and (app / "migrations").exists():
            clear_migration_files(app)


def connect_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        return conn
    except Exception as e:
        logging.error(f"Could not connect to database: {e}")
        sys.exit(1)


def clear_django_migrations_table(conn):
    with conn.cursor() as cur:
        logging.info(f"Clearing table: {DJANGO_MIGRATIONS_TABLE}")
        cur.execute(f"DELETE FROM {DJANGO_MIGRATIONS_TABLE};")
        conn.commit()
        logging.info("Migration history cleared.")


def drop_and_recreate_db():
    # Connect to the default 'postgres' database to drop and recreate the target DB
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            logging.warning(f"Dropping database: {DB_NAME}")
            cur.execute(
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s;",
                (DB_NAME,),
            )
            cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
            logging.info(f"Creating database: {DB_NAME}")
            cur.execute(f"CREATE DATABASE {DB_NAME};")
        conn.close()
        logging.info("Database dropped and recreated.")
    except Exception as e:
        logging.error(f"Error dropping/creating database: {e}")
        sys.exit(1)


def main():
    drop_db = "--drop-db" in sys.argv
    noinput = "--noinput" in sys.argv

    logging.warning(
        "This script will irreversibly reset migration history and (optionally) the database."
    )
    if not noinput:
        if not confirm("Are you sure you want to proceed? [y/N]: "):
            logging.info("Aborted by user.")
            sys.exit(0)
        if drop_db and not confirm(
            "Are you REALLY sure you want to DROP and RECREATE the database? [y/N]: "
        ):
            logging.info("Aborted by user.")
            sys.exit(0)

    if drop_db:
        drop_and_recreate_db()
    else:
        conn = connect_db()
        clear_django_migrations_table(conn)
        conn.close()

    clear_all_migrations(APPS_DIR)
    logging.info("Migration files cleared for all apps.")

    logging.info("Reset complete. Next steps:")
    logging.info(
        "1. Run `python manage.py makemigrations` to generate fresh migrations."
    )
    logging.info("2. Run `python manage.py migrate` to apply migrations.")
    logging.info("3. Recreate any superusers or test data as needed.")


if __name__ == "__main__":
    main()
