# Generated by Django 5.0.6 on 2024-12-29 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notebook', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notebook',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='notebook',
            name='slug',
            field=models.SlugField(max_length=100),
        ),
    ]
