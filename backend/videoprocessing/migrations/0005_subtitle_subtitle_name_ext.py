# Generated by Django 5.1.1 on 2024-09-18 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videoprocessing', '0004_alter_subtitle_subtitle_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='subtitle_name_ext',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
