# pylint: skip-file
# Generated by Django 3.2.10 on 2022-02-17 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simple_messaging', '0003_auto_20211012_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='outgoingmessage',
            name='message_metadata',
            field=models.TextField(blank=True, null=True),
        ),
    ]
