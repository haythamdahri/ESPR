# Generated by Django 2.0.5 on 2018-06-02 18:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appelsOffres', '0002_auto_20180602_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annonce',
            name='datePub',
            field=models.DateTimeField(default=datetime.datetime(2018, 6, 2, 18, 48, 25, 352154), null=True),
        ),
    ]
