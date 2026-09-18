from django.db import migrations


ADMIN_GROUP_NAME = "NEXCODE_ADMIN"


def create_nexcode_admin_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")

    Group.objects.get_or_create(
        name=ADMIN_GROUP_NAME,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_nexcode_admin_group,
            migrations.RunPython.noop,
        ),
    ]