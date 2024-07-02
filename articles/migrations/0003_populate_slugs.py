# Generated by Django 5.0.6 on 2024-07-02 09:07

from django.db import migrations, models
import random
import string
from django.utils.text import slugify

from articles.models import Article

def generate_unique_slug(title, Post):
    if title:
        base_slug = slugify(title)
    else:
        base_slug = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    slug = base_slug
    while Article.objects.filter(slug=slug).exists():
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        slug = f"{base_slug}-{random_string}"
    return slug

def populate_slugs(apps, schema_editor):
    Post = apps.get_model('articles', 'Article')
    for post in Post.objects.all():
        if not post.slug:
            post.slug = generate_unique_slug(post.title, Post)
            post.save()


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_article_slug'),
    ]

    operations = [
        migrations.RunPython(populate_slugs),
    ]
