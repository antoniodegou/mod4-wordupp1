# Generated by Django 4.2.3 on 2023-09-01 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0004_subscription_stripe_subscription_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='stripe_plan_id',
            field=models.CharField(choices=[('free_plan_id_here', 'Free'), ('premium_plan_id_here', 'Premium')], default='free_plan_id_here', max_length=50),
        ),
    ]
