# Generated by Django 4.1 on 2022-09-02 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_alter_auctionlisting_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='picture',
            field=models.URLField(blank=True),
        ),
    ]
