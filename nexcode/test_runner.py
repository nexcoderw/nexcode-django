from django.db import connections
from django.db.backends.base.creation import TEST_DATABASE_PREFIX
from django.test.runner import DiscoverRunner


NEON_POOLER_MARKER = "-pooler."


class DirectConnectionTestRunner(DiscoverRunner):
    """Create and drop the test database without interference.

    The configured DATABASE_URL may point at Neon's transaction pooler
    (PgBouncer). The pooler keeps its own server connection to the test
    database open after Django disconnects, so ``DROP DATABASE`` fails
    with "database is being accessed by other users".

    Two measures prevent that:

    * Test runs use Neon's direct endpoint, which is the same host
      without the ``-pooler`` suffix. Schema operations such as creating
      and dropping a database belong there, not on the pooler.
    * Before the test database is created, and again before it is
      dropped, any other session still attached to it is closed, so a
      session left over from an earlier interrupted run cannot block it.

    Only the test run is affected; the application keeps using the
    pooled connection it is configured with.
    """

    def setup_databases(self, **kwargs):
        for alias in connections:
            use_direct_endpoint(alias)

            connection = connections[alias]

            if connection.vendor == "postgresql":
                # Nothing is created yet, so resolve the name the test
                # database is about to be given.
                close_other_test_sessions(
                    alias,
                    connection.creation._get_test_db_name(),
                )

        return super().setup_databases(**kwargs)

    def teardown_databases(self, old_config, **kwargs):
        for alias in connections:
            connection = connections[alias]

            if connection.vendor != "postgresql":
                continue

            # By teardown Django has already switched NAME to the test
            # database, so the current name is the one to clear. The
            # runner's own connection is closed cleanly first rather than
            # terminated from outside.
            test_name = connection.settings_dict["NAME"]

            connection.close()

            close_other_test_sessions(alias, test_name)

        return super().teardown_databases(old_config, **kwargs)


def use_direct_endpoint(alias):
    connection = connections[alias]

    if connection.vendor != "postgresql":
        return

    host = connection.settings_dict.get("HOST") or ""

    if NEON_POOLER_MARKER not in host:
        return

    # Drop any connection already opened through the pooler before the
    # host changes underneath it.
    connection.close()

    connection.settings_dict["HOST"] = host.replace(
        NEON_POOLER_MARKER,
        ".",
        1,
    )

    # Server-side cursors were only disabled because the transaction
    # pooler cannot support them; the direct endpoint can.
    connection.settings_dict["DISABLE_SERVER_SIDE_CURSORS"] = False


def close_other_test_sessions(alias, test_name):
    """Terminate every other session attached to the test database.

    Only ever touches a database whose name carries Django's test prefix,
    so a misconfigured TEST name can never close sessions on a real one.
    """
    connection = connections[alias]

    if not test_name.startswith(TEST_DATABASE_PREFIX):
        return

    # The maintenance connection is not attached to the test database,
    # so it never counts as one of the sessions being closed.
    with connection._nodb_cursor() as cursor:
        cursor.execute(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s
              AND pid <> pg_backend_pid()
            """,
            [test_name],
        )
