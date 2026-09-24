from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0042_payment_reminders'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='paymentreminderrule',
            name='unique_payment_reminder_rule',
        ),
        migrations.RemoveConstraint(
            model_name='paymentreminderrule',
            name='payment_reminder_valid_timing',
        ),
        migrations.AddField(
            model_name='paymentreminderrule',
            name='remind_on',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='paymentreminderrule',
            name='timing',
            field=models.CharField(choices=[('before', 'Before'), ('on', 'On'), ('after', 'After'), ('date', 'On a set date')], max_length=10),
        ),
        migrations.AddConstraint(
            model_name='paymentreminderrule',
            constraint=models.UniqueConstraint(condition=models.Q(('remind_on__isnull', True)), fields=('agreement', 'event', 'timing', 'days', 'channel'), name='unique_payment_reminder_rule'),
        ),
        migrations.AddConstraint(
            model_name='paymentreminderrule',
            constraint=models.UniqueConstraint(condition=models.Q(('timing', 'date')), fields=('agreement', 'event', 'remind_on', 'channel'), name='unique_payment_reminder_date_rule'),
        ),
        migrations.AddConstraint(
            model_name='paymentreminderrule',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('days', 0), ('remind_on__isnull', True), ('timing', 'on')), models.Q(('days__gt', 0), ('remind_on__isnull', True), ('timing__in', ('before', 'after'))), models.Q(('days', 0), ('remind_on__isnull', False), ('timing', 'date')), _connector='OR'), name='payment_reminder_valid_timing'),
        ),
    ]
