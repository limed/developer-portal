# Generated by Django 2.2.1 on 2019-05-15 15:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='date',
            field=models.DateField(default=datetime.date.today, verbose_name='Article date'),
        ),
    ]
