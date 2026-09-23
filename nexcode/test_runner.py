from django.db import connections
from django.test.runner import DiscoverRunner


NEON_POOLER_MARKER = "-pooler."


class DirectConnectionTestRunner(DiscoverRunner):
    """Run the test database over Neon's direct endpoint.

    The configured DATABASE_URL may point at Neon's transaction pooler
    (PgBouncer). The pooler keeps its own server connection to the test
    database open after Django disconnects, so the final
    ``DROP DATABASE`` fails with "database is being accessed by other
    users". Schema operations such as creating and dropping a database
    belong on the direct endpoint, which is the same host without the
    ``-pooler`` suffix.

    Only the test run is affected; the application keeps using the
    pooled connection it is configured with.
    """

    def setup_databases(self, **kwargs):
        for alias in connections:
            use_direct_endpoint(alias)

        return super().setup_databases(**kwargs)


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
