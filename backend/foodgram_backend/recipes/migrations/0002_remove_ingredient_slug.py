# Generated by Django 3.2.3 on 2023-12-26 20:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='slug',
        ),
    ]