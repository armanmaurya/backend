# Generated by Django 5.0.6 on 2024-06-16 19:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0007_remove_article_id_alter_article_uuid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='uuid',
            new_name='id',
        ),
    ]