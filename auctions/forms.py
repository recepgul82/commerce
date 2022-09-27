from django import forms
from .models import AuctionListing, Bid, Comment


class ListingForm(forms.ModelForm):

    class Meta:
        model = AuctionListing
        fields = "__all__"
        exclude = ["creator", "date", "watchlist", "status", "winner", "max_price"]


class BiddingForm(forms.ModelForm):

    class Meta:
        model = Bid
        fields = ["bidding_price"]

