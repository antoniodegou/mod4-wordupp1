# Generated by Django 4.2.3 on 2023-08-31 11:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_alter_subscription_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 30, 11, 54, 40, 396229)),
        ),
    ]
