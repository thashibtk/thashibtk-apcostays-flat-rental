# Generated by Django 5.1.5 on 2025-01-29 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RegisterDb',
            fields=[
                ('UserID', models.AutoField(primary_key=True, serialize=False)),
                ('Name', models.CharField(blank=True, max_length=100, null=True)),
                ('Email', models.EmailField(blank=True, max_length=100, null=True)),
                ('Password', models.CharField(blank=True, max_length=100, null=True)),
                ('ConfirmPassword', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
