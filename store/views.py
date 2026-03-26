from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Product, Cart, Message, Profile


# =====================
# HOME
# =====================

def home(request):

    search = request.GET.get("search")

    if search:
        products = Product.objects.filter(name__icontains=search)
    else:
        products = Product.objects.all()

    return render(request, "home.html", {
        "products": products
    })


# =====================
# PRODUCT DETAIL
# =====================

def product_detail(request, id):

    product = get_object_or_404(Product, id=id)

    return render(request, "product.html", {
        "product": product
    })


# =====================
# REGISTER BUYER
# =====================

def register_view(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = User.objects.create_user(
            username=username,
            password=password
        )

        profile = Profile.objects.get(user=user)
        profile.role = "buyer"
        profile.save()

        return redirect("/login/")

    return render(request,"register.html")


# =====================
# REGISTER SELLER
# =====================

def register_seller(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = User.objects.create_user(
            username=username,
            password=password
        )

        profile = Profile.objects.get(user=user)
        profile.role = "seller"
        profile.save()

        return redirect("/login/")

    return render(request,"register.html")


# =====================
# LOGIN
# =====================

def login_view(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect("/")

    return render(request, "login.html")


# =====================
# LOGOUT
# =====================

def logout_view(request):

    logout(request)
    return redirect("/")


# =====================
# CART
# =====================

@login_required
def add_to_cart(request, id):

    product = get_object_or_404(Product, id=id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("/cart")


@login_required
def view_cart(request):

    cart_items = Cart.objects.filter(user=request.user)

    total = 0

    for item in cart_items:
        total += item.product.price * item.quantity

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total
    })

# =====================
# CART ACTIONS
# =====================

@login_required
def remove_from_cart(request, id):

    item = get_object_or_404(Cart, id=id, user=request.user)
    item.delete()

    return redirect("/cart")


@login_required
def increase_quantity(request, id):

    item = get_object_or_404(Cart, id=id, user=request.user)

    item.quantity += 1
    item.save()

    return redirect("/cart")


@login_required
def decrease_quantity(request, id):

    item = get_object_or_404(Cart, id=id, user=request.user)

    item.quantity -= 1

    if item.quantity <= 0:
        item.delete()
    else:
        item.save()

    return redirect("/cart")
    
# =====================
# CHAT
# =====================

@login_required
def chat(request,user_id):

    other_user = get_object_or_404(User,id=user_id)

    messages = Message.objects.filter(
        Q(sender=request.user,receiver=other_user) |
        Q(sender=other_user,receiver=request.user)
    ).order_by("created")


    if request.method == "POST":

        text = request.POST.get("text")

        Message.objects.create(
            sender=request.user,
            receiver=other_user,
            content=text
        )

        return redirect("chat",user_id=other_user.id)

    return render(request,"chat.html",{
        "messages":messages,
        "other_user":other_user
    })


# =====================
# SELLER DASHBOARD
# =====================

@login_required
def seller_dashboard(request):

    if request.user.profile.role != "seller":
        return redirect("/")

    products = Product.objects.filter(owner=request.user)

    return render(request, "seller_dashboard.html", {
        "products": products
    })


# =====================
# SELLER ADD PRODUCT
# =====================

def seller_add(request):

    if request.method == "POST":

        name = request.POST["name"]
        price = request.POST["price"]
        image = request.FILES.get("image")

        Product.objects.create(
            name=name,
            price=price,
            image=image,
            seller=request.user
        )

    products = Product.objects.filter(owner=request.user)

    return render(request, "seller_add.html", {
        "products": products
    })

def delete_product(request, id):

    product = get_object_or_404(Product, id=id)

    # chỉ cho chủ sản phẩm xoá
    if product.owner == request.user:
        product.delete()

    return redirect("/seller/add/")

#====================
# SELLER CHAT LIST
#====================
@login_required
def seller_chat_list(request):

    messages = Message.objects.filter(receiver=request.user)

    users = []

    for m in messages:
        if m.sender not in users:
            users.append(m.sender)

    return render(request,"seller_chat_list.html",{
        "users":users
    })

# =====================
# ADMIN DASHBOARD
# =====================

@staff_member_required
def dashboard(request):

    products = Product.objects.all()

    return render(request, "dashboard.html", {
        "products": products
    })


# =====================
# ADMIN ADD PRODUCT
# =====================

@staff_member_required
def add_product(request):

    if request.method == "POST":

        name = request.POST["name"]
        price = request.POST["price"]
        image = request.FILES.get("image")

        Product.objects.create(
            owner=request.user,
            name=name,
            price=price,
            image=image
        )

        return redirect("/dashboard/")

    return render(request, "add_product.html")


# =====================
# ADMIN DELETE PRODUCT
# =====================

@staff_member_required
def delete_product(request, id):

    if not request.user.is_authenticated:
        return redirect("/login/")

    product = get_object_or_404(Product, id=id)

    if product.owner == request.user:
        product.delete()

    return redirect("/seller/add/")

# =====================
# CHECKOUT
# =====================

@login_required
def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)

    total = 0
    for item in cart_items:
        total += item.product.price * item.quantity

    from .models import Order, OrderItem

    order = Order.objects.create(
        user=request.user,
        total=total
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity
        )
        # 👇 THÔNG BÁO CHO NGƯỜI BÁN
        Notification.objects.create(
            user=item.product.owner,
            message=f"Có người đặt {item.product.name} (SL: {item.quantity})"
        )

    cart_items.delete()

    return redirect("/orders/")


# =====================
# ORDERS
# =====================

@login_required
def orders(request):

    from .models import Order

    orders = Order.objects.filter(user=request.user)

    return render(request, "orders.html", {
        "orders": orders
    })

# =====================
# ADMIN EDIT PRODUCT
# =====================

@staff_member_required
def edit_product(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":

        product.name = request.POST["name"]
        product.price = request.POST["price"]

        if request.FILES.get("image"):
            product.image = request.FILES["image"]

        product.save()

        return redirect("/dashboard/")

    return render(request, "edit_product.html", {
        "product": product
    })
