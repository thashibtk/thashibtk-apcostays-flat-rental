# Generated by Django 5.1.5 on 2025-01-30 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0002_remove_registerdb_phone_remove_registerdb_place_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registerdb',
            name='ConfirmPassword',
        ),
        migrations.AddField(
            model_name='registerdb',
            name='username',
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
    ]
