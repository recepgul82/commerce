from genericpath import exists
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import ListingForm, BiddingForm
from django.db.models import Max

from .models import User, AuctionListing, Category, Bid, Comment


def index(request):
    return render(request, "auctions/index.html", {
        #"active_listing": AuctionListing.objects.filter(status__exact = True)
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
    request = request
    number_of_bids = len(listing.bids_on_item.all())
    
    if listing.status != True:
        if listing.winner != user_id:
            message = "Auction Closed!"
        else:
            message = "Congratulations! You won the auction"
    else:
        message = f"There are currently {number_of_bids} bids on the item!"

    if user_id == "None":
        return render(request, "auctions/listing.html", {
            "listing": listing,
        })  
          
    else: 
        user = User.objects.get(pk=user_id)
        
        try:
            watchlist = user.watchlist_items.get(pk=listing_id)
        except AuctionListing.DoesNotExist:
            watchlist= None
        
        if request.method == "POST" and request.POST.get("watchlist_status"):
            # Checks the item and adds or removes an item from the watchlist
            return watchlist_status(request, user, user_id, listing_id, watchlist, listing)

        elif request.method == "POST" and request.POST.get("bidding_price"):
            return bidding(request, user_id, listing_id, watchlist, listing, user, number_of_bids)
        
        elif request.method == "POST" and request.POST.get("closed"):
            return close_auction(request, listing_id, user_id, listing, watchlist, message)
        
        elif request.method == "POST" and request.POST.get("comment"):
            return post_comment(request, user_id, listing_id)

        else: 
            comments = AuctionListing.objects.get(pk=listing_id).comments.all() 
            print(listing_id)
            print(comments)
            bidding_form = BiddingForm() 
            return render(request, "auctions/listing.html", { 
                "watchlist": watchlist,
                "listing": listing,
                "bidding_form": bidding_form,
                "message": message,
                "comments": comments,
            })


@login_required()
def post_comment(request, user_id, listing_id):
    text = request.POST.get("comment")
    print(text)
    
    comment = Comment(comment_item=AuctionListing.objects.get(pk=listing_id), commentor=User.objects.get(pk=user_id), comment_text=text)
    comment.save()

    return HttpResponseRedirect(reverse("listing", kwargs={
            'listing_id': listing_id,
            'user_id': user_id,
            }))


@login_required()
def close_auction(request, listing_id, user_id, listing, watchlist, message):
    print((request.POST.get("closed")))
    closed = request.POST.get("closed")

    if closed == "True":
        listing.status = False
        message = "Auction Closed"

        # find the max amount on a bid
        bid = AuctionListing.objects.get(id=listing_id)
        bids = bid.bids_on_item.all()
        max = bids.all().aggregate(Max("bidding_price"))
        listing.max_price = max["bidding_price__max"]
        # find the max bid object
        max_bid = bids.get(bidding_price = listing.max_price)
        # update winner on the listing
        listing.winner = max_bid.bidder
        listing.save()

    return render(request, "auctions/listing.html", { 
        "watchlist": watchlist,
        "listing": listing,
        "message": message,
        "comments": AuctionListing.objects.get(pk=listing_id).comments.all() 
    })

       
@login_required()
def watchlist_status(request, user, user_id, listing_id, watchlist, listing):
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


@login_required()   
def bidding(request, user_id, listing_id, watchlist, listing, user, number_of_bids):
    print("bidding info success")
    bidding_form = BiddingForm(request.POST)
    if bidding_form.is_valid():
        
        bid = Bid(bidder=user, bidding_price = bidding_form.cleaned_data["bidding_price"], bid_item = listing)
        if bid.bidding_price <= listing.price:
            message = "Bidding should be greater than the current price"
            
        else:  
            bid.save()    
            message = f"Bidding successful! There are currently {number_of_bids} number of bids on the item!"
            return HttpResponseRedirect(reverse("listing", kwargs={
            'listing_id': listing_id,
            'user_id': user_id,
            }))

    bidding_form = BiddingForm()
    
    return render(request, "auctions/listing.html", { 
        "watchlist": watchlist,
        "listing": listing,
        "bidding_form": bidding_form,
        "message": message,
    })


def watchlist(request, user_id):
    user = User.objects.get(id=user_id)
    return render(request, "auctions/watchlist.html", {
        "listings": user.watchlist_items.all(),
    })

