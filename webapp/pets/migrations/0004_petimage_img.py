# Generated by Django 2.0.7 on 2018-07-04 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0003_auto_20180704_0902'),
    ]

    operations = [
        migrations.AddField(
            model_name='petimage',
            name='img',
            field=models.ImageField(default='images/blank.png', upload_to='images/'),
        ),
    ]
