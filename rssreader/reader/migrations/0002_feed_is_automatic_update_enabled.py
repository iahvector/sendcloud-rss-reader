# Generated by Django 4.2.1 on 2023-05-26 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='is_automatic_update_enabled',
            field=models.BooleanField(default=True),
        ),
    ]