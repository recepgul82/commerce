from genericpath import exists
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import ListingForm, BiddingForm

from .models import User, AuctionListing, Category


def index(request):
    return render(request, "auctions/index.html", {
        "active_listing": AuctionListing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required()
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        user_id = request.POST["creator"]
        if form.is_valid():
            listing_name = form.cleaned_data["listing_name"]
            definition = form.cleaned_data["definition"]
            price = form.cleaned_data["price"]
            picture = form.cleaned_data["picture"]
            category = form.cleaned_data["category"].pk
        
            listing = AuctionListing(
                listing_name=listing_name, 
                definition=definition, 
                price=price, 
                picture=picture,
                category=Category(pk=category),
                creator=User(pk=user_id)
                )
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = ListingForm()
        #assign form here
    return render(request, "auctions/create_listing.html", {
        "form": form
    })


def listing(request, listing_id, user_id):
    listing = AuctionListing.objects.get(id=listing_id)
    user = User.objects.get(pk=user_id)

    try:
        watchlist = user.watchlist_items.get(pk=listing_id)
    except AuctionListing.DoesNotExist:
        watchlist= None
    
    if request.method == "POST" and request.POST.get("watchlist_status"):
        print((request.POST.get("watchlist_status")))

        watchlist_status = request.POST["watchlist_status"]
        # Return False if the item is already on watchlist
        if watchlist_status == "True":   
            user.watchlist_items.add(listing)
            # adds the item to the users watchlist 
            return HttpResponseRedirect(reverse("listing", kwargs={
            'listing_id': listing_id,
            'user_id': user_id
            }))
        else:
            user.watchlist_items.remove(watchlist)
            #removes the item from the users watchlist
            return HttpResponseRedirect(reverse("listing", kwargs={
            'listing_id': listing_id,
            'user_id': user_id
            }))

    elif request.method == "POST" and request.POST.get("bidding_price"):
        print("bidding info success")
        bidding_form = BiddingForm(request.POST)
        if bidding_form.is_valid():
            bidding_price = bidding_form.cleaned_data["bidding_price"]
            if bidding_price <= listing.price:
                message = "Bidding should be greater than the price"
                
            else:  
                listing.price = bidding_price
                listing.save()
                message = "Bidding successful!"

        bidding_form = BiddingForm() 
        return render(request, "auctions/listing.html", { 
            "watchlist": watchlist,
            "listing": listing,
            "bidding_form": bidding_form,
            "message": message
        })
    
        
    else: 
        bidding_form = BiddingForm() 
        return render(request, "auctions/listing.html", { 
            "watchlist": watchlist,
            "listing": listing,
            "bidding_form": bidding_form,
        })


    
