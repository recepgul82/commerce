# Generated by Django 4.1 on 2022-09-01 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_alter_auctionlisting_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='picture',
            field=models.ImageField(upload_to='auctions/media/'),
        ),
    ]
