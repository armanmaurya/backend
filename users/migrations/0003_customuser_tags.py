# Generated by Django 5.0.6 on 2024-06-26 06:20

import taggit.managers
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
        ('users', '0002_customuser_registration_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
