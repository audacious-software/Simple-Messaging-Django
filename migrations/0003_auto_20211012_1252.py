# pylint: skip-file
# Generated by Django 3.2.7 on 2021-10-12 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simple_messaging', '0002_auto_20210616_1045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingmessage',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='incomingmessagemedia',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='outgoingmessage',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
