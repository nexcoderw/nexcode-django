from django.db import migrations


class Migration(migrations.Migration):
    """Reduce clients to name, email, and phone number.

    ``phone`` is renamed rather than dropped and re-added, so any stored
    phone numbers carry over. The status constraint is removed before the
    status column it checks.
    """

    dependencies = [
        ('home', '0036_alter_team_image_png'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='client',
            name='client_valid_status',
        ),
        migrations.RenameField(
            model_name='client',
            old_name='phone',
            new_name='phone_number',
        ),
        migrations.RemoveField(
            model_name='client',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='client',
            name='company_name',
        ),
        migrations.RemoveField(
            model_name='client',
            name='website',
        ),
        migrations.RemoveField(
            model_name='client',
            name='location',
        ),
        migrations.RemoveField(
            model_name='client',
            name='profile_image',
        ),
        migrations.RemoveField(
            model_name='client',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='client',
            name='status',
        ),
    ]
