# NOTE: This module is not currently used in the project as we are using supabase for database operations.
# It is kept for future reference and potential use in the future.
# This module provides utilities for managing database connections, optimizing queries,
# handling migrations, backups, and performing health checks on the database.

from django.conf import settings
from django.db import connections
from django.core.exceptions import ImproperlyConfigured
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database connection manager for handling multiple database connections
    and providing database-related utilities.
    """

    @staticmethod
    def get_connection(alias="default"):
        """Get a database connection by alias."""
        return connections[alias]

    @staticmethod
    def close_connections():
        """Close all database connections."""
        connections.close_all()

    @staticmethod
    def test_connection(alias="default"):
        """Test database connection health."""
        try:
            connection = connections[alias]
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed for {alias}: {e}")
            return False

    @staticmethod
    def get_connection_info(alias="default"):
        """Get database connection information."""
        try:
            connection = connections[alias]
            return {
                "vendor": connection.vendor,
                "database": connection.settings_dict.get("NAME"),
                "host": connection.settings_dict.get("HOST"),
                "port": connection.settings_dict.get("PORT"),
                "user": connection.settings_dict.get("USER"),
            }
        except Exception as e:
            logger.error(f"Failed to get connection info for {alias}: {e}")
            return None


class DatabaseOptimizer:
    """
    Database optimization utilities for query performance monitoring
    and connection pool management.
    """

    @staticmethod
    def analyze_slow_queries(threshold_ms=1000):
        """
        Analyze slow queries above the specified threshold.
        This would typically integrate with database-specific tools.
        """
        # Implementation would depend on database backend
        # For PostgreSQL, you might query pg_stat_statements
        # For development, we'll use Django's connection queries
        from django.db import connection

        slow_queries = []
        if hasattr(connection, "queries"):
            for query in connection.queries:
                time_taken = float(query.get("time", 0)) * 1000
                if time_taken > threshold_ms:
                    slow_queries.append(
                        {
                            "sql": query["sql"],
                            "time_ms": time_taken,
                        }
                    )

        return slow_queries

    @staticmethod
    def get_connection_pool_stats():
        """Get connection pool statistics."""
        stats = {}
        for alias in connections:
            try:
                connection = connections[alias]
                # Basic connection info
                stats[alias] = {
                    "is_usable": connection.is_usable(),
                    "vendor": connection.vendor,
                    "in_atomic_block": connection.in_atomic_block,
                }

                # Add pool-specific stats if available
                if hasattr(connection, "pool"):
                    pool = connection.pool
                    stats[alias].update(
                        {
                            "pool_size": getattr(pool, "size", "N/A"),
                            "checked_out": getattr(pool, "checked_out", "N/A"),
                            "overflow": getattr(pool, "overflow", "N/A"),
                        }
                    )

            except Exception as e:
                stats[alias] = {"error": str(e)}

        return stats


class DatabaseMigrationHelper:
    """
    Helper utilities for database migrations and schema management.
    """

    @staticmethod
    def check_migration_status():
        """Check the status of database migrations."""
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection

        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())

        return {
            "unapplied_migrations": len(plan),
            "migrations": [
                f"{migration.app_label}.{migration.name}"
                for migration, backwards in plan
            ],
        }

    @staticmethod
    def get_applied_migrations():
        """Get list of applied migrations."""
        from django.db.migrations.recorder import MigrationRecorder

        recorder = MigrationRecorder(connections["default"])
        applied = recorder.applied_migrations()

        return [f"{app}.{name}" for app, name in applied]


class DatabaseBackupHelper:
    """
    Helper utilities for database backup operations.
    """

    @staticmethod
    def create_backup_info():
        """Create backup metadata information."""
        from django.utils import timezone

        db_info = DatabaseManager.get_connection_info()
        if not db_info:
            return None

        return {
            "timestamp": timezone.now().isoformat(),
            "database": db_info["database"],
            "host": db_info["host"],
            "vendor": db_info["vendor"],
            "migration_status": DatabaseMigrationHelper.check_migration_status(),
        }

    @staticmethod
    def validate_backup_environment():
        """Validate that backup environment is properly configured."""
        required_settings = [
            "DATABASES",
        ]

        missing_settings = []
        for setting in required_settings:
            if not hasattr(settings, setting):
                missing_settings.append(setting)

        if missing_settings:
            raise ImproperlyConfigured(
                f"Missing required settings for backup: {missing_settings}"
            )

        return True


class DatabaseHealthChecker:
    """
    Database health monitoring utilities.
    """

    @staticmethod
    def comprehensive_health_check():
        """Perform comprehensive database health check."""
        results = {}

        for alias in connections:
            results[alias] = DatabaseHealthChecker.check_database_health(alias)

        return results

    @staticmethod
    def check_database_health(alias="default"):
        """Check health of a specific database connection."""
        health_info = {
            "alias": alias,
            "status": "unknown",
            "connection_test": False,
            "response_time_ms": None,
            "error": None,
        }

        try:
            import time

            start_time = time.time()

            # Test basic connectivity
            health_info["connection_test"] = DatabaseManager.test_connection(alias)

            # Measure response time
            end_time = time.time()
            health_info["response_time_ms"] = round((end_time - start_time) * 1000, 2)

            # Determine overall status
            if health_info["connection_test"]:
                if health_info["response_time_ms"] < 100:
                    health_info["status"] = "healthy"
                elif health_info["response_time_ms"] < 500:
                    health_info["status"] = "degraded"
                else:
                    health_info["status"] = "slow"
            else:
                health_info["status"] = "unhealthy"

        except Exception as e:
            health_info["status"] = "error"
            health_info["error"] = str(e)
            logger.error(f"Database health check failed for {alias}: {e}")

        return health_info


class DatabaseSecurityHelper:
    """
    Database security-related utilities.
    """

    @staticmethod
    def validate_connection_security():
        """Validate database connection security settings."""
        warnings = []

        for alias, config in settings.DATABASES.items():
            # Check for SSL usage in production
            if not settings.DEBUG:
                options = config.get("OPTIONS", {})
                if "sslmode" not in options:
                    warnings.append(f"Database {alias}: SSL not configured")

            # Check for weak passwords (basic check)
            password = config.get("PASSWORD", "")
            if len(password) < 12:
                warnings.append(f"Database {alias}: Weak password detected")

        return warnings

    @staticmethod
    def get_database_permissions():
        """Get database user permissions (PostgreSQL specific)."""
        from django.db import connection

        if connection.vendor != "postgresql":
            return {"error": "Only supported for PostgreSQL"}

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        rolname,
                        rolsuper,
                        rolcreaterole,
                        rolcreatedb,
                        rolcanlogin
                    FROM pg_roles
                    WHERE rolname = current_user
                """
                )

                row = cursor.fetchone()
                if row:
                    return {
                        "username": row[0],
                        "is_superuser": row[1],
                        "can_create_role": row[2],
                        "can_create_db": row[3],
                        "can_login": row[4],
                    }

        except Exception as e:
            logger.error(f"Failed to get database permissions: {e}")

        return {"error": "Failed to retrieve permissions"}


# Singleton instances for easy access
db_manager = DatabaseManager()
db_optimizer = DatabaseOptimizer()
db_migration_helper = DatabaseMigrationHelper()
db_backup_helper = DatabaseBackupHelper()
db_health_checker = DatabaseHealthChecker()
db_security_helper = DatabaseSecurityHelper()
