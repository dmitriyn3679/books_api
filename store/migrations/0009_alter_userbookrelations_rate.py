# Generated by Django 4.0.3 on 2022-03-18 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_rename_is_bookmarks_userbookrelations_in_bookmarks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbookrelations',
            name='rate',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Bad'), (2, 'Well'), (3, 'Good'), (4, 'Very good'), (5, 'Amazing')], null=True),
        ),
    ]
