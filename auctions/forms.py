from django import forms
from .models import AuctionListing


class ListingForm(forms.ModelForm):

    class Meta:
        model = AuctionListing
        fields = "__all__"
        exclude = ["creator", "date"]

