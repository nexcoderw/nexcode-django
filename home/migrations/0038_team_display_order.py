from django.db import migrations, models


def number_members_alphabetically(apps, schema_editor):
    """Give existing members positions 1..N in their current order.

    The public team page listed members by name, so numbering them that
    way keeps the site unchanged on deploy, and gives the admin real
    positions to edit rather than a column of zeros.
    """
    Team = apps.get_model("home", "Team")

    members = Team.objects.order_by("name", "pk").only("pk")

    for position, member in enumerate(members, start=1):
        Team.objects.filter(pk=member.pk).update(display_order=position)


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0037_simplify_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='display_order',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.RunPython(
            number_members_alphabetically,
            migrations.RunPython.noop,
        ),
        migrations.AlterModelOptions(
            name='team',
            options={
                'ordering': ('display_order', 'name', 'pk'),
                'verbose_name': 'Team Member',
                'verbose_name_plural': 'Team Members',
            },
        ),
    ]
