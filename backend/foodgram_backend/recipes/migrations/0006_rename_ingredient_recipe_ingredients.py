# Generated by Django 3.2.3 on 2023-12-27 08:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_rename_tag_recipe_tags'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='ingredient',
            new_name='ingredients',
        ),
    ]