from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0039_contact'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='user_agent',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AddField(
            model_name='contact',
            name='device_type',
            field=models.CharField(choices=[('desktop', 'Desktop'), ('mobile', 'Mobile'), ('tablet', 'Tablet'), ('bot', 'Bot'), ('unknown', 'Unknown')], default='unknown', max_length=20),
        ),
        migrations.AddField(
            model_name='contact',
            name='browser',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='contact',
            name='operating_system',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='contact',
            name='replied_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.CreateModel(
            name='ContactReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='home.contact')),
                ('sent_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contact_replies', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Contact reply',
                'verbose_name_plural': 'Contact replies',
                'ordering': ('-sent_at', '-pk'),
            },
        ),
    ]
