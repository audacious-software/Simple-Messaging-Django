# pylint: skip-file
# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-06-17 13:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IncomingMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient', models.CharField(max_length=256)),
                ('receive_date', models.DateTimeField()),
                ('message', models.TextField(max_length=1024)),
                ('transmission_metadata', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='IncomingMessageMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField(default=0)),
                ('content_file', models.FileField(blank=True, null=True, upload_to='incoming_message_media')),
                ('content_url', models.CharField(blank=True, max_length=1024, null=True)),
                ('content_type', models.CharField(default='application/octet-stream', max_length=128)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media', to='simple_messaging.IncomingMessage')),
            ],
        ),
        migrations.CreateModel(
            name='OutgoingMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('destination', models.CharField(max_length=256)),
                ('reference_id', models.IntegerField(blank=True, null=True)),
                ('send_date', models.DateTimeField()),
                ('sent_date', models.DateTimeField(blank=True, null=True)),
                ('message', models.TextField(max_length=1024)),
                ('errored', models.BooleanField(default=False)),
                ('transmission_metadata', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
