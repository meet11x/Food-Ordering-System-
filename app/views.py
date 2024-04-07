from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Users, MenuItems, CartItem, Restaurants
from datetime import datetime


def index(request):
    return render(request, "index.html", {})


def user_register(request):
    return render(request, "register.html")


def registered(request):
    if request.method == "POST":
        uname = request.POST.get("username")
        pass1 = request.POST.get("password")
        pass2 = request.POST.get("password1")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        userType = request.POST.get("userType")

        if pass1 != pass2:
            messages.error(request, "Your password isn't matching !!")
            return redirect("register")
        else:
            my_user = Users.objects.create_user(
                username=uname,
                email=email,
                password=pass1,
                Phone=phone,
                Address=address,
                UserType=userType,
            )
            my_user.save()
            messages.success(request, "Successfully signup done !!! \n Please login")
            return redirect("login")
    else:
        return render(request, "index.html", {})


def logindone(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "successful login...")
            return redirect("index")
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return redirect("login")
    else:
        return render(request, "index.html")


def user_login(request):
    return render(request, "login.html", {})


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("index")


@login_required
def user_profile(request):
    return render(request, "user_profile.html", {})


def aboutUs(request):
    return render(request, "aboutUs.html")


def popularDishes(request):
    items = MenuItems.objects.all()
    return render(request, "popular_dishes.html", {"items": items})


def Search(request):
    search = request.GET.get("search")
    if search:
        # results = request.POST.get('search')
        # Q-like query |-or
        # results = MenuItems.objects.filter(
        #     Q(Name_icontains=search)
        #     | Q(Description__icontains=search)
        #     | Q(Price_icontains=search)
        #     | Q(RestaurantID_icontains=search)
        # )
        results = MenuItems.objects.filter(
            Q(Name__icontains=search) | Q(Price__icontains=search)
        )
        # alldishes={'items':items_with_restaurant_names}
    else:
        results = None
    return render(
        request, "popular_dishes.html", {"results": results, "search": search}
    )


@login_required
def add_to_cart(request, item_id):
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user
        item = MenuItems.objects.get(pk=item_id)
        # Check if the item already exists in the user's cart
        cart_item = CartItem.objects.filter(user=user, item=item).first()
        if cart_item:
            cart_item.quantity += 1
            cart_item.save()
        else:
            CartItem.objects.create(user=user, item=item)
        messages.success(request, "Item added to cart successfully")
        return redirect("view_cart")
    else:
        messages.error(request, "Please login to add to cart")
        return redirect("login")


@login_required
def view_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart_items = CartItem.objects.filter(user=user)
        total_price = sum(item.subtotal() for item in cart_items)
        if cart_items.exists():
            return render(
                request,
                "view_cart.html",
                {"cart_items": cart_items, "total_price": total_price},
            )
        else:
            status = True
            return render(request, "view_cart.html", {"status": status})
    else:
        messages.error(request, "Please login to view cart")
        return redirect("login")


def offline_way(request):
    type_of_payment = request.GET.get("paymentmethod")
    user = request.user
    address = user.Address
    cart = CartItem.objects.filter(user=user)
    cartcopy = CartItem.objects.filter(user=user).filter(
        id__in=cart.values_list("id", flat=True)
    )
    total_price = sum(item.subtotal() for item in cartcopy)
    cart.delete()
    context = {"address": address, "cart": cartcopy, "total_price": total_price}
    return render(request, "offline.html", context)


def online_way(request):
    type_of_payment = request.GET.get("paymentmethod")
    user = request.user
    address = user.Address
    cart = CartItem.objects.filter(user=user)
    total_price = sum(item.subtotal() for item in cart)
    context = {"address": address, "cart": cart, "total_price": total_price}
    # return render(request, "index.html", {})
    return render(request, "online.html", context)


def orderconfirm(request):
    if request.method == "POST":
        username = request.POST.get("username")
        cardnumber = request.POST.get("cardnumber")
        date = request.POST.get("date")
        year, month, day = date.split("-")
        user = request.user
        usernameforbill = user.username
        year = int(year)
        month = int(month)
        day = int(day)
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        current_day = now.day
        dateforbill = (
            str(current_day) + "-" + str(current_month) + "-" + str(current_year)
        )
        current_time = datetime.now().time()
        cvc = request.POST.get("cvc")
        # positive = "We are thrilled to inform you that your order has been successfully placed. Our team is already hard at work to ensure that your items are carefully prepared and promptly delivered to you."
        # negative = "Apologies, the input provided appears to be incorrect. Please review and try again. Thank you for your understanding"
        if len(username) != 0:

            if (
                len(cardnumber) == 12
                and compareDate(
                    year, month, day, current_year, current_month, current_day
                )
                and len(cvc) == 3
                and checkname(username)
            ):

                user = request.user
                cart_items = CartItem.objects.filter(user=user)
                total_price = sum(item.subtotal() for item in cart_items)
                # cartcopy = deepcopy(cart_items)
                if cart_items:
                    cart_items.delete()

                return render(
                    request,
                    "orderconfirm.html",
                    {
                        "status": True,
                        "time": current_time,
                        "username": usernameforbill,
                        "date": dateforbill,
                        "totalprice": total_price,
                    },
                )
            else:
                # positive = "Apologies, the input provided appears to be incorrect. Please review and try again. Thank you for your understanding"

                return render(
                    request,
                    "orderconfirm.html",
                    {"status": False},
                )
    return render(request, "gotoorder.html", {})


def checkname(username):
    for i in username:
        if i.isdigit():
            return False
    return True


def compareDate(year, month, day, current_year, current_month, current_day):
    if year > int(current_year):
        return True
    elif year == int(current_year):
        if month > int(current_month):
            return True
        elif month == int(current_month):
            if day > int(current_day):
                return True
            else:
                return False
    else:
        return False


def makepayment(request):
    type_of_payment = request.POST.get("paymentmethod")
    user = request.user
    address = user.Address
    cart = CartItem.objects.filter(user=user)
    total_price = sum(item.subtotal() for item in cart)
    context = {"address": address, "cart": cart, "total_price": total_price}
    if request.method == "POST":
        # type_of_payment = request.POST.get("paymentmethod")
        if type_of_payment == "online":
            return render(request, "online.html", {})
        elif type_of_payment == "offline":
            return render(request, "offline.html", context)

    return render(request, "index.html", {})


@login_required
def remove_from_cart(request, item_id):
    if request.method == "POST":
        user = request.user
        item = MenuItems.objects.get(pk=item_id)
        cart_item = CartItem.objects.filter(user=user, item=item).first()
        if cart_item:
            cart_item.delete()
    return redirect("view_cart")


def gotoorder(request):

    if request.method == "POST":
        user = request.user
        cart = CartItem.objects.filter(user=user)
        total_price = sum(item.subtotal() for item in cart)
        context = {"total_price": total_price}
        if cart.exists():
            return render(request, "gotoorder.html", context)
        else:
            m = True
            return render(request, "view_cart.html", {"message": m})
    else:
        return render(request, "index.html", {})


def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(
        CartItem, id=item_id
    )  # used to get object from databse
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()
    return redirect("view_cart")


def increase_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect("view_cart")
