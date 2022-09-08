# Generated by Django 4.1 on 2022-09-06 12:13

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0015_alter_auctionlisting_watchlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='watchlist',
            field=models.ManyToManyField(blank=True, related_name='watchlist_items', to=settings.AUTH_USER_MODEL),
        ),
    ]
