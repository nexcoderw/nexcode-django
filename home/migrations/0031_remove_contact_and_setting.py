from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0030_remove_blog_author_remove_blog_tags_and_more"),
    ]

    operations = [
        migrations.DeleteModel(name="Contact"),
        migrations.DeleteModel(name="Setting"),
    ]
