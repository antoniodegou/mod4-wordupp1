# Generated by Django 4.2.3 on 2023-08-31 11:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 30, 11, 52, 57, 60209)),
        ),
    ]
