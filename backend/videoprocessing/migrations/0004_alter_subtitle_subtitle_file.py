# Generated by Django 5.1.1 on 2024-09-18 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videoprocessing', '0003_remove_subtitle_video_file_subtitle_video_file_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subtitle',
            name='subtitle_file',
            field=models.BinaryField(),
        ),
    ]
