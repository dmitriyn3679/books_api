# Generated by Django 4.0.3 on 2022-03-12 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_rename_books_book'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='author_name',
            field=models.CharField(default='author', max_length=255),
            preserve_default=False,
        ),
    ]
