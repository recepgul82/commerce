from django import forms
from .models import AuctionListing, Bid


class ListingForm(forms.ModelForm):

    class Meta:
        model = AuctionListing
        fields = "__all__"
        exclude = ["creator", "date"]


class BiddingForm(forms.ModelForm):

    class Meta:
        model = Bid
        fields = ["bidding_price"]