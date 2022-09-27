from datetime import datetime
from tkinter import CASCADE
from xmlrpc.client import Boolean
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass
    

class Category(models.Model):
    category_name = models.CharField(max_length=16)

    def __str__(self):
        return f"{self.category_name}"


class AuctionListing(models.Model):
    listing_name = models.CharField(max_length=32)
    definition = models.CharField(max_length=120)
    price = models.IntegerField()
    picture = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="categories")
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now)
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist_items")
    status = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank= True, null = True, related_name="bid_winners")
    max_price = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.listing_name}"


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidders")
    bidding_price = models.IntegerField()
    bid_item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids_on_item")

    def __str__(self):
        return f"{self.bidder} bid {self.bidding_price}$ on {self.bid_item.listing_name}"


class Comment(models.Model):
    comment_item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    commentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commentors")
    comment_text = models.CharField(max_length=200)

    def __str__(self):
        return f"comment on {self.comment_item} by {self.commentor}"




