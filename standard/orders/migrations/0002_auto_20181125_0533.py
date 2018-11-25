# Generated by Django 2.1.3 on 2018-11-25 05:33

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='queue',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.Queue'),
        ),
        migrations.AddField(
            model_name='order',
            name='created',
            field=models.DateTimeField(auto_created=True, blank=True, default=datetime.datetime(2018, 11, 25, 5, 33, 28, 535388)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customer',
            name='created',
            field=models.DateTimeField(auto_created=True, blank=True),
        ),
    ]
