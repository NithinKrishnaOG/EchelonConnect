# Generated by Django 4.2.7 on 2023-12-13 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='video',
            field=models.FileField(default=1, upload_to='post_images'),
            preserve_default=False,
        ),
    ]
