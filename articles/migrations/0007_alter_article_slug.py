# Generated by Django 5.0.6 on 2024-07-02 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0006_alter_article_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='slug',
            field=models.SlugField(max_length=255, unique=True),
        ),
    ]
