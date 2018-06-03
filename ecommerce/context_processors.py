import datetime

from django.db.models import Max
from django.shortcuts import get_object_or_404

from ecommerce.models import WishList, Compare, CommerceCategory, Sale, Tag, Cart, Shop


def global_var(request):
    user = request.user

    # ---------------- number items in wishlist
    if user.is_authenticated:
        number_items_wish_list = WishList.objects.filter(user__user=user).count()
    else:
        number_items_wish_list = 0

    # ---------------- is supplier
    supplier = False
    store = None
    if user.is_authenticated:
        profil = user.profil
        if profil.is_professional and profil.is_supplier:
            if Shop.objects.filter(owner=profil).exists():
                store = get_object_or_404(Shop, owner=profil).id
                supplier = True

    # ---------------- is seller
    seller = False
    if user.is_authenticated:
        profil = user.profil
        if profil.is_seller:
            seller = True

    # ---------------- number items in compare
    if user.is_authenticated:
        number_items_compare = Compare.objects.filter(user__user=user).count()
    else:
        number_items_compare = 0

    # --------------- All Categories ---------------
    categories = CommerceCategory.objects.all()

    # --------------- Hot Categories ---------------
    hot_categories = list()
    featured_sale = Sale.objects.filter(date_end__gte=datetime.date.today()).values(
        'product__cat__category_two__category_one__category') \
                        .annotate(Max('percentage')).order_by('-percentage__max')[:6]
    for el in featured_sale:
        cat = CommerceCategory.objects.get(pk=el["product__cat__category_two__category_one__category"])
        hot_categories.append(cat)
        el["product__cat__category_two__category_one__category"] = cat
    # Complete 4 categories
    count = len(hot_categories)
    if count < 4:
        for i in range(0, CommerceCategory.objects.count()):
            category_to_add = CommerceCategory.objects.all()[i]
            if category_to_add not in hot_categories:
                hot_categories.append(category_to_add)
            if len(hot_categories) == 4:
                break
    hot_categories = hot_categories

    # --------------- All Tags ---------------
    tags = Tag.objects.all()

    # --------------- Cart ---------------
    my_cart_result = my_cart(user)
    number_products_in_cart = my_cart_result['number_products_in_cart']
    total_price_in_cart = my_cart_result['total_price_in_cart']
    cart_result = my_cart_result['cart']

    context = {
        # for base.html
        'categories': categories,
        'number_items_wish_list': number_items_wish_list,
        'number_items_compare': number_items_compare,
        'hot_categories': hot_categories[:4],
        'featured_sale': featured_sale,
        'tags': tags,
        'cart': cart_result,
        'total_price_in_cart': total_price_in_cart,
        'number_products_in_cart': number_products_in_cart,
        'is_supplier': supplier,
        'is_seller': seller,
        'store_id': store
    }

    return context


def my_cart(user):
    number_products_in_cart = 0
    total_price_in_cart = 0
    cart_result = None
    if user.is_authenticated:
        cart_result = Cart.objects.filter(user=user.profil)
        for el in cart_result:
            stock = el.product.stock_set.filter(color=el.color).exclude(color__name__exact="None")
            if stock.exists():
                el.product.price = el.product.price + stock.all()[0].price_sup
            number_products_in_cart += 1
            sale = el.product.sale_set.filter(date_end__gte=datetime.date.today())
            if sale.exists():
                el.product.price = el.product.price - ((el.product.price * sale.all()[0].percentage) / 100)
            total_price_in_cart += (el.product.price * el.quantity)
    return {'cart': cart_result, 'number_products_in_cart': number_products_in_cart, 'total_price_in_cart': total_price_in_cart}