from django.conf import settings
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from ecommerce.forms import *
from .models import *
from django.db.models import Max, Avg, Sum, Q, Count
from django.db.models.functions import Lower
from django.utils import timezone
from decimal import Decimal, Inexact
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt
import datetime


def index(request):
    hide_menu = True
    # --------------- All Brands with images---------------
    brands = Brand.objects.exclude(image='')

    # --------------- Slides ---------------
    slides = Slide.objects.filter(active=True, product__active=True, product__approved=True).order_by('date_add')

    # --------------- Featured Sale ---------------
    featured_sale = my_featured_sale()['featured_sale']

    # --------------- Daily Deals ---------------
    daily_deals = Sale.objects.filter(is_daily=True).values('id').filter(product__active=True, product__approved=True).annotate(
        ratting=Avg('product__commerceratting__value'))
    for el in daily_deals:
        sale = Sale.objects.get(pk=el['id'])
        if el['ratting']:
            el['rattingInt'] = int(el['ratting'])
        else:
            el['rattingInt'] = 0
            el['ratting'] = 0
        el['id'] = sale
        el['quantity'] = el["id"].product.stock_set.aggregate(Sum('quantity'))["quantity__sum"]
        el['first_quantity'] = el["id"].product.stock_set.aggregate(Sum('first_quantity'))["first_quantity__sum"]
        el['percent'] = (el['quantity'] * 100) / el['first_quantity']
        el['sold'] = el['first_quantity'] - el['quantity']

    # --------------- Best Selling Products ---------------
    best_selling = OrderLine.objects.values('product__id').filter(product__active=True, product__approved=True).annotate(quantity=Sum('quantity')).order_by('-quantity')[:10]
    # convert to list
    best_selling = list(best_selling)
    # Complete 10 products
    count = len(best_selling)
    if count < 10:
        for i in range(0, Product.objects.filter(active=True, approved=True).count()):
            product_to_add = {'product__id': Product.objects.filter(active=True, approved=True).all()[i].id, 'quantity': 0}
            if product_to_add not in best_selling:
                best_selling.append(product_to_add)
            if len(best_selling) == 10:
                break
    # treatement
    for el in best_selling:
        product = Product.objects.get(pk=el['product__id'])
        el['product__id'] = product
        if (datetime.date.today() - product.date_add).days < 30:
            el['is_new'] = True
        else:
            el['is_new'] = False
        ratting = product.commerceratting_set.aggregate(ratting=Avg('value'))
        el['ratting'] = ratting['ratting']
        if el['ratting']:
            el['rattingInt'] = int(el['ratting'])
        else:
            el['rattingInt'] = 0
            el['ratting'] = 0
        sale = product.sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
        if sale.exists():
            el['sale'] = sale[0]
        else:
            el['sale'] = None

    # --------------- Most Viewed Products ---------------
    most_viewed = list()

    products_viewed = Product.objects.filter(active=True, approved=True).order_by('-number_views')[:8]
    #    CommerceRatting.objects.values('product__id').annotate(views=Count('id'), ratting=Avg('value')).order_by('-views')
    for el in products_viewed:
        ob = dict()
        ob['product'] = el
        # ratting average
        ratting = el.commerceratting_set.aggregate(ratting=Avg('value'))
        if ratting['ratting'] is not None:
            ob['ratting'] = ratting['ratting']
            ob['rattingInt'] = int(ratting['ratting'])
        else:
            ob['ratting'] = 0
            ob['rattingInt'] = 0
        most_viewed.append(ob)
        del ob

    context = {
        'hide_menu': hide_menu,
        'slides': slides,
        'featured_sale': featured_sale,
        'daily_deals': daily_deals,
        'best_selling': best_selling,
        'most_viewed': most_viewed,
        'brands': brands,
    }
    return render(request, 'ecommerce/index.html', context)


def search(request):
    # Initialisation
    category_id = category = word = list_products = min_value = max_value = number_elements = sort_by = None
    brands_id = colors_id = page_range = []
    type_search = "All"
    is_pro = 'both'
    filter_by_price = is_filtered = False
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        word = request.POST.get('word')
        min_value = request.POST.get('min_val')
        max_value = request.POST.get('max_val')
        colors_id = request.POST.getlist('color')
        brands_id = request.POST.getlist('brand')
        is_filtered = request.POST.get('filter')
        filter_by_price = request.POST.get('price')
        is_pro = request.POST.get('is_pro')
        page = request.POST.get('page', 1)
        number_elements = request.POST.get('number_elements', 15)
        sort_by = request.POST.get("sort_by", "1")

        # Stock dans une session
        if is_filtered:
            if colors_id:
                request.session['colors_id'] = colors_id
            else:
                try:
                    del request.session['colors_id']
                except KeyError:
                    print('exception de suppression session colors')
            if brands_id:
                request.session['brands_id'] = brands_id
            else:
                try:
                    del request.session['brands_id']
                except KeyError:
                    print('exception de suppression session brands')
        elif 'colors_id' in request.session:
            colors_id = request.session['colors_id']
        elif 'brands_id' in request.session:
            colors_id = request.session['brands_id']

        if category_id:
            request.session['category_id'] = category_id
        elif 'category_id' in request.session:
            category_id = request.session['category_id']

        if word:
            request.session['word'] = word
        elif 'word' in request.session:
            word = request.session['word']

        products_results = Product.objects.filter(Q(name__icontains=word) | Q(tags__name__icontains=word), active=True, approved=True)
        print(is_pro)
        if is_pro == 'pro':
            products_results = products_results.filter(is_pro=True)
        elif is_pro == 'ord':
            products_results = products_results.filter(is_pro=False)
        if sort_by == "2":
            products_results = products_results.order_by(Lower("name"))
        elif sort_by == "3":
            products_results = products_results.order_by(Lower('name')).reverse()
        elif sort_by == "4":
            products_results = products_results.order_by('price')
        elif sort_by == "5":
            products_results = products_results.order_by('-price')
        elif sort_by == "8":
            products_results = products_results.order_by(Lower('brand__name'))
        elif sort_by == "9":
            products_results = products_results.order_by(Lower('brand__name')).reverse()
        elif sort_by == "10":
            products_results = products_results.order_by('-date_add')
        elif sort_by == "11":
            products_results = products_results.order_by('date_add')
        if products_results.exists():
            if category_id[0] == '-':
                products_results = products_results.filter(cat_id=category_id[1:])
                category = CommerceSCategory.objects.get(pk=category_id[1:])
                type_search = "sub_category"
            elif category_id[0] == '$':
                products_results = products_results.filter(cat__category_two__category_one_id=category_id[1:])
                category = CommerceSCategoryOne.objects.get(pk=category_id[1:])
                type_search = "category_one"
            elif category_id[0] == '*':
                products_results = products_results.filter(cat__category_two_id=category_id[1:])
                category = CommerceSCategoryTwo.objects.get(pk=category_id[1:])
                type_search = "category_two"
            elif not category_id == '0':
                products_results = products_results.filter(cat__category_two__category_one__category_id=category_id)
                category = CommerceCategory.objects.get(pk=category_id)
                type_search = "category"

            # ----------------- filter by range price
            if filter_by_price:
                if max_value:
                    request.session['max_value'] = max_value
                    try:
                        Decimal(max_value)
                        products_results = products_results.filter(price__lte=max_value)
                    except Inexact:
                        print('exception conversion')
                else:
                    max_value = request.session['max_value']
                    try:
                        Decimal(max_value)
                        products_results = products_results.filter(price__lte=max_value)
                    except Inexact:
                        print('exception conversion')
                if min_value:
                    if min_value:
                        request.session['min_value'] = min_value
                        try:
                            Decimal(min_value)
                            products_results = products_results.filter(price__gte=min_value)
                        except Inexact:
                            print('exception conversion')
                    else:
                        min_value = request.session['min_value']
                        try:
                            Decimal(min_value)
                            products_results = products_results.filter(price__gte=min_value)
                        except Inexact:
                            print('exception conversion')

            # --------------- filter by colors
            if colors_id:
                products_results = products_results.filter(stock__color_id__in=colors_id)

            # --------------- filter by brands
            if brands_id:
                products_results = products_results.filter(brand_id__in=brands_id)

            # select id, Avg(value) from product inner join commerce_ratting
            products_results = products_results.values('id').annotate(ratting=Avg('commerceratting__value'))
            if sort_by == "6":
                products_results = products_results.order_by('-ratting')
            if sort_by == "7":
                products_results = products_results.order_by('ratting')

            for el in products_results:
                product = Product.objects.get(pk=el['id'])
                el['id'] = product

                if el['ratting']:
                    el['rattingInt'] = int(el['ratting'])
                else:
                    el['rattingInt'] = 0
                    el['ratting'] = 0

                if (timezone.localtime(timezone.now()).date() - product.date_add).days < 30:
                    el['new'] = True
                else:
                    el['new'] = False

                sale = product.sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
                if sale.exists():
                    el['sale'] = sale[0]
                else:
                    el['sale'] = None
                if product.stock_set.exists():
                    el['quantity'] = product.stock_set.aggregate(quantity=Sum('quantity'))["quantity"]
                    el['first_quantity'] = product.stock_set.aggregate(quantity=Sum('first_quantity'))["quantity"]
                else:
                    el['quantity'] = 0
                    el['first_quantity'] = 0

                images = CommerceImage.objects.filter(product=product)
                if images.exists():
                    el['image'] = images[0].image
                else:
                    el['image'] = None

                el['sold'] = el['first_quantity'] - el['quantity']

            paginator = Paginator(products_results, number_elements)
            try:
                list_products = paginator.page(page)
            except PageNotAnInteger:
                list_products = paginator.page(1)
            except EmptyPage:
                list_products = paginator.page(paginator.num_pages)

            # range for display just 7 numbers
            index_page = list_products.number - 1
            max_index = len(paginator.page_range)
            start_index = index_page - 4 if index_page >= 4 else 0
            end_index = index_page + 4 if index_page <= max_index - 4 else max_index
            page_range = list(paginator.page_range)[start_index:end_index]
    # ------------------ colors, brands ------------------
    colors = Color.objects.all()
    brands = Brand.objects.all()
    if category_id:
        if category_id[0] == '-':
            colors = colors.filter(stock__product__cat_id=category_id[1:]).distinct()
            brands = brands.filter(product__cat__id=category_id[1:]).distinct()
        elif category_id[0] == '$':
            colors = colors.filter(stock__product__cat__category_two__category_one_id=category_id[1:]).distinct()
            brands = brands.filter(product__cat__category_two__category_one_id=category_id[1:]).distinct()
        elif category_id[0] == '*':
            colors = colors.filter(stock__product__cat__category_two_id=category_id[1:]).distinct()
            brands = brands.filter(product__cat__category_two_id=category_id[1:]).distinct()
        elif not category_id == '0' and not category_id == "+":
            colors = colors.filter(stock__product__cat__category_two__category_one__category__id=category_id).distinct()
            brands = brands.filter(product__cat__category_two__category_one__category__id=category_id).distinct()
    context = {
        'results': list_products,
        'colors': colors,
        'brands': brands,

        'category': category,
        'type_search': type_search,
        'word': word,
        'selected_colors': list(map(int, colors_id)),
        'selected_brands': list(map(int, brands_id)),
        'filter_by_price': filter_by_price,
        'is_filtered': is_filtered,
        'max_value': max_value,
        'min_value': min_value,
        'page_range': page_range,
        'sort_by': sort_by,
        'number_elements': number_elements,
        'is_pro': is_pro
    }
    return render(request, 'ecommerce/search.html', context)


def products(request, type_search="all", id_search="0"):
    # ---------------- Featured brands
    brands = Brand.objects.exclude(image='').values('id').annotate(number=Count('product__id')).order_by('number')
    for el in brands:
        brand = Brand.objects.get(pk=el['id'])
        el['id'] = brand

    # Initialisation
    list_products = category = None
    products_results = Product.objects.filter(id__lte=-1)
    page_range = []
    found = True
    page = request.POST.get('page', 1)
    number_elements = request.POST.get('number_elements', 15)
    sort_by = request.POST.get("sort_by", "1")

    message = "Achetez par"
    name = "All"
    if type_search == "all":
        products_results = Product.objects.filter(active=True, approved=True)
    elif type_search == "tag":
        tags_s = Tag.objects.filter(pk=id_search)
        if tags_s.exists():
            products_results = Product.objects.filter(tags__id__exact=id_search, active=True, approved=True)
            message = "Achetez par: {}".format(tags_s[0].name)
            name = tags_s[0].name
        else:
            found = False
    elif type_search == "brand":
        brands_s = Brand.objects.filter(pk=id_search)
        if brands_s.exists():
            products_results = Product.objects.filter(brand_id__exact=id_search, active=True, approved=True)
            message = "Achetez par : {}".format(brands_s[0].name)
            name = brands_s[0].name
        else:
            found = False
    elif type_search == "sub_category":
        sub_categories_s = CommerceSCategory.objects.filter(pk=id_search)
        if sub_categories_s.exists():
            products_results = Product.objects.filter(cat_id__exact=id_search, active=True, approved=True)
            message = "Achetez par : {}".format(sub_categories_s[0].name)
            name = sub_categories_s[0].name
            category = sub_categories_s[0]
        else:
            found = False

    elif type_search == "category_two":
        sub_categories_s = CommerceSCategoryTwo.objects.filter(pk=id_search)
        if sub_categories_s.exists():
            products_results = Product.objects.filter(cat__category_two_id__exact=id_search, active=True, approved=True)
            message = "Achetez par : {}".format(sub_categories_s[0].name)
            name = sub_categories_s[0].name
            category = sub_categories_s[0]
        else:
            found = False
    elif type_search == "category_one":
        sub_categories_s = CommerceSCategoryOne.objects.filter(pk=id_search)
        if sub_categories_s.exists():
            products_results = Product.objects.filter(cat__category_two__category_one_id__exact=id_search, active=True, approved=True)
            message = "Achetez par : {}".format(sub_categories_s[0].name)
            name = sub_categories_s[0].name
            category = sub_categories_s[0]
        else:
            found = False
    elif type_search == "category":
        categories_s = CommerceCategory.objects.filter(pk=id_search)
        if categories_s.exists():
            products_results = Product.objects.filter(cat__category_two__category_one__category_id__exact=id_search, active=True, approved=True)
            message = "Achetez par : {}".format(categories_s[0].name)
            name = categories_s[0].name
            category = categories_s[0]
        else:
            found = False
    else:
        found = False

    if sort_by == "2":
        products_results = products_results.order_by(Lower("name"))
    elif sort_by == "3":
        products_results = products_results.order_by(Lower('name')).reverse()
    elif sort_by == "4":
        products_results = products_results.order_by('price')
    elif sort_by == "5":
        products_results = products_results.order_by('-price')
    elif sort_by == "8":
        products_results = products_results.order_by(Lower('brand__name'))
    elif sort_by == "9":
        products_results = products_results.order_by(Lower('brand__name')).reverse()
    elif sort_by == "10":
        products_results = products_results.order_by('-date_add')
    elif sort_by == "11":
        products_results = products_results.order_by('date_add')
    if products_results.exists():
        # select id, Avg(value) from product inner join commerce_ratting
        products_results = products_results.values('id').annotate(ratting=Avg('commerceratting__value'))
        if sort_by == "6":
            products_results = products_results.order_by('-ratting')
        if sort_by == "7":
            products_results = products_results.order_by('ratting')

        for el in products_results:
            product = Product.objects.get(pk=el['id'])
            el['id'] = product

            if el['ratting']:
                el['rattingInt'] = int(el['ratting'])
            else:
                el['rattingInt'] = 0
                el['ratting'] = 0

            if (timezone.localtime(timezone.now()).date() - product.date_add).days < 30:
                el['new'] = True
            else:
                el['new'] = False

            sale = product.sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
            if sale.exists():
                el['sale'] = sale[0]
            else:
                el['sale'] = None

            if product.stock_set.exists():
                el['quantity'] = product.stock_set.aggregate(quantity=Sum('quantity'))["quantity"]
                el['first_quantity'] = product.stock_set.aggregate(quantity=Sum('first_quantity'))["quantity"]
            else:
                el['quantity'] = 0
                el['first_quantity'] = 0

            images = CommerceImage.objects.filter(product=product)
            if images.exists():
                el['image'] = images[0].image
            else:
                el['image'] = None

            el['sold'] = el['first_quantity'] - el['quantity']

        paginator = Paginator(products_results, number_elements)
        try:
            list_products = paginator.page(page)
        except PageNotAnInteger:
            list_products = paginator.page(1)
        except EmptyPage:
            list_products = paginator.page(paginator.num_pages)

        # range for display just 11 numbers
        index_page = list_products.number - 1
        max_index = len(paginator.page_range)
        start_index = index_page - 5 if index_page >= 4 else 0
        end_index = index_page + 5 if index_page <= max_index - 4 else max_index
        page_range = list(paginator.page_range)[start_index:end_index]
    if found is False:
        message = "Désolé nous n'avons pas troucvé ce '{}'".format(type_search)
        list_products = None
    context = {
        'results': list_products,
        'brands': brands,
        'type_search': type_search,
        'id_search': id_search,
        'message': message,
        'name': name,
        'category': category,

        'page_range': page_range,
        'sort_by': sort_by,
        'number_elements': number_elements,
    }
    return render(request, 'ecommerce/products.html', context)


def your_products(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('main_app:log_in'))
    if not user.profil.is_supplier:
        return HttpResponseRedirect(reverse('e_commerce:index'))
    else:
        # Initialisation
        category = None
        page_range = []
        found = True
        page = request.POST.get('page', 1)
        number_elements = request.POST.get('number_elements', 15)
        sort_by = request.POST.get("sort_by", "1")

        if user.profil.is_supplier:
            products_results = Product.objects.filter(supplier=user.profil.shop, active=True, approved=True)
        else:
            products_results = Product.objects.filter(active=True, approved=True)
        if not products_results.exists():
            found = False
        if found:
            if sort_by == "2":
                products_results = products_results.order_by(Lower("name"))
            elif sort_by == "3":
                products_results = products_results.order_by(Lower('name')).reverse()
            elif sort_by == "4":
                products_results = products_results.order_by('price')
            elif sort_by == "5":
                products_results = products_results.order_by('-price')
            elif sort_by == "6":
                products_results = products_results.order_by(Lower('brand__name'))
            elif sort_by == "7":
                products_results = products_results.order_by(Lower('brand__name')).reverse()
            elif sort_by == "8":
                products_results = products_results.order_by('-date_add')
            elif sort_by == "9":
                products_results = products_results.order_by('date_add')

            paginator = Paginator(products_results, number_elements)
            try:
                list_products = paginator.page(page)
            except PageNotAnInteger:
                list_products = paginator.page(1)
            except EmptyPage:
                list_products = paginator.page(paginator.num_pages)

            # range for display just 11 numbers
            index_page = list_products.number - 1
            max_index = len(paginator.page_range)
            start_index = index_page - 5 if index_page >= 4 else 0
            end_index = index_page + 5 if index_page <= max_index - 4 else max_index
            page_range = list(paginator.page_range)[start_index:end_index]
        else:
            list_products = None
        message_warning = None
        if 'message_warning' in request.session:
            message_warning = request.session['message_warning']
            del request.session['message_warning']
        context = {
            'results': list_products,
            'category': category,
            'message_warning': message_warning,

            'page_range': page_range,
            'sort_by': sort_by,
            'number_elements': number_elements,
        }
        return render(request, 'ecommerce/list_product.html', context)


def remove_product(request):
    user = request.user
    print('1')
    if not user.is_authenticated:
        print('2')
        return HttpResponseRedirect(reverse('main_app:log_in'))
    if not user.profil.is_supplier:
        print('3')
        return HttpResponseRedirect(reverse('e_commerce:index'))
    if request.method == "POST":
        print('4')
        product_id = request.POST.get('product', '')
        if product_id:
            print('5')
            product_l = Product.objects.filter(pk=product_id)
            if product_l.exists():
                print('6')
                product = product_l[0]
                product.active = False
                product.save()
                return HttpResponseRedirect(reverse('e_commerce:your_products'))
            else:
                return HttpResponseRedirect(reverse('e_commerce:index'))
        else:
            return HttpResponseRedirect(reverse('e_commerce:index'))
    else:
        return HttpResponseRedirect(reverse('e_commerce:index'))


def list_categories(request):
    categories = all_categories()
    # ------------ Categories with number -------------------
    categories_2 = list()
    for category in categories:

        category_one_2 = list()
        for category_one in category.commercescategoryone_set.all():

            category_two_2 = list()
            for category_two in category_one.commercescategorytwo_set.all():

                sub_category_2 = list()
                for sub_category in category_two.commercescategory_set.all():
                    sub_one = {'sub_category': sub_category,
                               'number': sub_category.product_set.filter(active=True, approved=True).aggregate(number=Count('id'))['number']}
                    sub_category_2.append(sub_one)

                ob_two = {'category_two': category_two, 'sub_category': sub_category_2,
                          'number': category_two.commercescategory_set.filter(product__active=True, product__approved=True).aggregate(number=Count('product__id'))['number']}
                category_two_2.append(ob_two)

            ob_one = {'category_one': category_one, 'category_two': category_two_2, 'number': category_one.commercescategorytwo_set.filter(commercescategory__product__active=True, commercescategory__product__approved=True).aggregate(number=Count('commercescategory__product__id'))['number']}
            category_one_2.append(ob_one)

        ob = {'category': category, 'category_one': category_one_2,
              'number': category.commercescategoryone_set.filter(commercescategorytwo__commercescategory__product__active=True, commercescategorytwo__commercescategory__product__approved=True).aggregate(
                  number=Count('commercescategorytwo__commercescategory__product__id'))['number']}
        categories_2.append(ob)

    # ----------- Latest products
    latest_products = Product.objects.filter(active=True, approved=True).order_by('-date_add')[:15]
    latest_products = latest_products.values('id').annotate(ratting=Avg('commerceratting__value'))
    for el in latest_products:
        p = Product.objects.get(pk=el['id'])
        el['id'] = p

        if el['ratting']:
            el['rattingInt'] = int(el['ratting'])
        else:
            el['rattingInt'] = 0
            el['ratting'] = 0

        sale_l = p.sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
        if sale_l.exists():
            el['sale'] = sale_l[0]
        else:
            el['sale'] = None

    context = {
        'latest_products': latest_products,
        'categories_2': categories_2
    }
    return render(request, 'ecommerce/all-categories.html', context)


def review(request):
    product_id = "1"
    if request.method == "POST":
        product_id = request.POST.get('product', None)
        name = request.POST.get('name', "")
        email = request.POST.get('email', "")
        value = request.POST.get('ratting', 3)
        comment = request.POST.get('review', "")
        if product_id:
            c = CommerceRatting()
            c.product = Product.objects.get(pk=product_id)
            c.value = value
            c.name = name
            c.email = email
            c.comment = comment
            c.save()
    return HttpResponseRedirect('/e_commerce/product/{}'.format(product_id))


def processing_orders(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('main_app:log_in'))
    if not user.profil.is_seller:
        return HttpResponseRedirect(reverse('e_commerce:index'))

    # ---------------- orders
    page = request.POST.get('page', 1)
    number_elements = request.POST.get('number_elements', 15)
    sort_by = request.POST.get("sort_by", "1")
    orders = Order.objects.filter(status="Processing")

    if sort_by == "2":
        orders = orders.order_by('id')
    if sort_by == "3":
        orders = orders.order_by('-id')
    if sort_by == "4":
        orders = orders.order_by('amount')
    if sort_by == "5":
        orders = orders.order_by('-amount')
    if sort_by == "6":
        orders = orders.order_by('date')
    if sort_by == "7":
        orders = orders.order_by('-date')

    paginator = Paginator(orders, number_elements)
    try:
        list_orders = paginator.page(page)
    except PageNotAnInteger:
        list_orders = paginator.page(1)
    except EmptyPage:
        list_orders = paginator.page(paginator.num_pages)

    # range for display just 7 numbers
    index_page = list_orders.number - 1
    max_index = len(paginator.page_range)
    start_index = index_page - 4 if index_page >= 4 else 0
    end_index = index_page + 4 if index_page <= max_index - 4 else max_index
    page_range = list(paginator.page_range)[start_index:end_index]

    context = {
        'orders': list_orders,
        'number_elements': number_elements,
        'sort_by': sort_by,
        'page_range': page_range
    }
    return render(request, 'ecommerce/processing-orders.html', context)


def update_order(request):
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            return HttpResponseRedirect(reverse('main_app:log_in'))
        if user.profil.is_seller:
            order_id = request.POST.get('order', None)
            track_number = request.POST.get('track_number', None)
            if order_id:
                order = Order.objects.get(pk=order_id)
                if track_number:
                    order.track_number = track_number
                order.status = "Shipped"
                order.date_complete = datetime.date.today()
                order.save()
                if order.payment_method == "Cash On Delivery":
                    order_line = OrderLine.objects.filter(order=order)
                    for el in order_line:
                        stock_results = Stock.objects.filter(product=el.product, color=el.color)
                        if stock_results.exists():
                            stock = stock_results[0]
                            stock.quantity = stock.quantity - el.quantity
                            stock.save()
                message = "<p>Salut,</p><p>Votre Commande <b>#{}</b> :</p>" \
                          "<p>Montant : <b>{}</b></p>" \
                          "<p>Date : <b>{}</b></p>" \
                          "<p>Méthode de Paiement : <b>{}</b></p>" \
                          "<p>Méthode de Livraison : <b>{}</b></p>" \
                          "<p>a été expédiée, votre Track Number : <b>{}</b>.</p><p>Merci.</p>".format(order.pk, order.amount, order.date, order.payment_method, order.delivery_method, track_number)
                send_mail(
                    'Commande #{}'.format(order.pk),
                    message,
                    'admin@socifly.com',
                    [order.user.user.email],
                    fail_silently=False,
                    html_message=message,
                )
                return HttpResponseRedirect(reverse('e_commerce:processing_orders'))
            else:
                return HttpResponseRedirect(reverse('e_commerce:index'))
        else:
            return HttpResponseRedirect(reverse('e_commerce:index'))
    else:
        return HttpResponseRedirect(reverse('e_commerce:index'))


def all_orders(request):
    user = request.user

    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('main_app:log_in'))
    if not user.profil.is_seller:
        return HttpResponseRedirect(reverse('e_commerce:index'))

    # ---------------- orders
    page = request.POST.get('page', 1)
    number_elements = request.POST.get('number_elements', 15)
    sort_by = request.POST.get("sort_by", "1")
    orders = Order.objects.all()
    total = orders.aggregate(amount=Sum('amount'))['amount']
    if sort_by == "2":
        orders = orders.order_by('id')
    if sort_by == "3":
        orders = orders.order_by('-id')
    if sort_by == "4":
        orders = orders.order_by('amount')
    if sort_by == "5":
        orders = orders.order_by('-amount')
    if sort_by == "6":
        orders = orders.order_by('date')
    if sort_by == "7":
        orders = orders.order_by('-date')

    paginator = Paginator(orders, number_elements)
    try:
        list_orders = paginator.page(page)
    except PageNotAnInteger:
        list_orders = paginator.page(1)
    except EmptyPage:
        list_orders = paginator.page(paginator.num_pages)

    # range for display just 7 numbers
    index_page = list_orders.number - 1
    max_index = len(paginator.page_range)
    start_index = index_page - 4 if index_page >= 4 else 0
    end_index = index_page + 4 if index_page <= max_index - 4 else max_index
    page_range = list(paginator.page_range)[start_index:end_index]

    context = {
        'orders': list_orders,
        'number_elements': number_elements,
        'sort_by': sort_by,
        'page_range': page_range,
        'total': total
    }
    return render(request, 'ecommerce/all-orders.html', context)


def products_sub(request, type_search, id_search):
    # ---------------- Featured brands
    brands = Brand.objects.exclude(image='').values('id').annotate(number=Count('product__id')).order_by('number')
    for el in brands:
        brand = Brand.objects.get(pk=el['id'])
        el['id'] = brand

    # ----------- Latest products
    latest_products = Product.objects.filter(active=True, approved=True).order_by('-date_add')[:15]
    latest_products = latest_products.values('id').annotate(ratting=Avg('commerceratting__value'))
    for el in latest_products:
        p = Product.objects.get(pk=el['id'])
        el['id'] = p

        if el['ratting']:
            el['rattingInt'] = int(el['ratting'])
        else:
            el['rattingInt'] = 0
            el['ratting'] = 0

        sale_l = p.sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
        if sale_l.exists():
            el['sale'] = sale_l[0]
        else:
            el['sale'] = None

    # Initialisation
    list_products = category = name = None
    products_results = Product.objects.filter(id__lte=-1)
    page_range = []
    found = True
    page = request.POST.get('page', 1)
    number_elements = request.POST.get('number_elements', 15)
    sort_by = request.POST.get("sort_by", "1")

    message = "Achetez par"
    sub_categories_s = CommerceSCategoryTwo.objects.filter(pk=id_search)
    if sub_categories_s.exists():
        products_results = Product.objects.filter(cat__category_two_id__exact=id_search, active=True, approved=True)
        message = "Achetez par : {}".format(sub_categories_s[0].name)
        name = sub_categories_s[0].name
        category = sub_categories_s[0]
    else:
        found = False

    if sort_by == "2":
        products_results = products_results.order_by(Lower("name"))
    elif sort_by == "3":
        products_results = products_results.order_by(Lower('name')).reverse()
    elif sort_by == "4":
        products_results = products_results.order_by('price')
    elif sort_by == "5":
        products_results = products_results.order_by('-price')
    elif sort_by == "8":
        products_results = products_results.order_by(Lower('brand__name'))
    elif sort_by == "9":
        products_results = products_results.order_by(Lower('brand__name')).reverse()
    elif sort_by == "10":
        products_results = products_results.order_by('-date_add')
    elif sort_by == "11":
        products_results = products_results.order_by('date_add')
    if products_results.exists():
        # select id, Avg(value) from product inner join commerce_ratting
        products_results = products_results.values('id').annotate(ratting=Avg('commerceratting__value'))
        if sort_by == "6":
            products_results = products_results.order_by('-ratting')
        if sort_by == "7":
            products_results = products_results.order_by('ratting')

        for el in products_results:
            product = Product.objects.get(pk=el['id'])
            el['id'] = product

            if el['ratting']:
                el['rattingInt'] = int(el['ratting'])
            else:
                el['rattingInt'] = 0
                el['ratting'] = 0

            if (timezone.localtime(timezone.now()).date() - product.date_add).days < 30:
                el['new'] = True
            else:
                el['new'] = False

            sale = product.sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
            if sale.exists():
                el['sale'] = sale[0]
            else:
                el['sale'] = None

            if product.stock_set.exists():
                el['quantity'] = product.stock_set.aggregate(quantity=Sum('quantity'))["quantity"]
                el['first_quantity'] = product.stock_set.aggregate(quantity=Sum('first_quantity'))["quantity"]
            else:
                el['quantity'] = 0
                el['first_quantity'] = 0

            images = CommerceImage.objects.filter(product=product)
            if images.exists():
                el['image'] = images[0].image
            else:
                el['image'] = None

            el['sold'] = el['first_quantity'] - el['quantity']

        paginator = Paginator(products_results, number_elements)
        try:
            list_products = paginator.page(page)
        except PageNotAnInteger:
            list_products = paginator.page(1)
        except EmptyPage:
            list_products = paginator.page(paginator.num_pages)

        # range for display just 11 numbers
        index_page = list_products.number - 1
        max_index = len(paginator.page_range)
        start_index = index_page - 5 if index_page >= 4 else 0
        end_index = index_page + 5 if index_page <= max_index - 4 else max_index
        page_range = list(paginator.page_range)[start_index:end_index]
    if found is False:
        message = "Désolé nous n'avons pas trouvé '{}'".format(type_search)
        list_products = None
    context = {
        'results': list_products,
        'brands': brands,
        'type_search': type_search,
        'id_search': id_search,
        'message': message,
        'name': name,
        'category': category,
        'latest_products': latest_products,

        'page_range': page_range,
        'sort_by': sort_by,
        'number_elements': number_elements,
    }
    return render(request, 'ecommerce/products_sub.html', context)


def display_product(request, id_product="0", message_success=None):
    # --------------------------- Product ---------------------------------
    if not Product.objects.filter(pk=id_product).exists():
        return HttpResponseRedirect('/e_commerce')
    product = Product.objects.get(pk=id_product)
    product.number_views += 1
    product.save()
    # ----------- Ratting
    ratting = Product.objects.filter(pk=id_product).aggregate(ratting=Avg('commerceratting__value'))['ratting']
    if ratting:
        ratting_int = int(ratting)
    else:
        ratting_int = 0
    # ----------- Sale
    sale = product.sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
    if sale.exists():
        sale = sale[0]
    else:
        sale = None
    if (timezone.localtime(timezone.now()).date() - product.date_add).days < 30:
        new = True
    else:
        new = False
    # ----------- Menu Categories
    menu_categories = product.cat.category_two.category_one.commercescategorytwo_set.values('id').annotate(
        number=Count('commercescategory__product__id'))
    for el in menu_categories:
        el['id'] = CommerceSCategoryTwo.objects.get(pk=el['id'])
    # ----------- Quantity
    quantity = product.stock_set.aggregate(Sum('quantity'))["quantity__sum"]
    if not quantity:
        quantity = 0
    first_quantity = product.stock_set.aggregate(Sum('first_quantity'))["first_quantity__sum"]
    if not first_quantity:
        first_quantity = 0
    if first_quantity == 0:
        percent = 0
    else:
        percent = (quantity * 100) / first_quantity
    sold = first_quantity - quantity
    # ----------- Accessories
    accessories = product.accessories.all()
    accessories = accessories.values('id').annotate(ratting=Avg('commerceratting__value'))
    for el in accessories:
        p = Product.objects.get(pk=el['id'])
        el['id'] = p

        if el['ratting']:
            el['rattingInt'] = int(el['ratting'])
        else:
            el['rattingInt'] = 0
            el['ratting'] = 0

        if (timezone.localtime(timezone.now()).date() - p.date_add).days < 15:
            el['new'] = True
        else:
            el['new'] = False

        sale_acc = p.sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
        if sale_acc.exists():
            el['sale'] = sale_acc[0]
        else:
            el['sale'] = None

        images = CommerceImage.objects.filter(product=p)
        if images.exists():
            el['image'] = images[0].image
        else:
            el['image'] = None

    # ----------- Latest products
    latest_products = Product.objects.all().order_by('-date_add')[:15]
    latest_products = latest_products.values('id').annotate(ratting=Avg('commerceratting__value'))
    for el in latest_products:
        p = Product.objects.get(pk=el['id'])
        el['id'] = p

        if el['ratting']:
            el['rattingInt'] = int(el['ratting'])
        else:
            el['rattingInt'] = 0
            el['ratting'] = 0

        sale_l = p.sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
        if sale_l.exists():
            el['sale'] = sale_l[0]
        else:
            el['sale'] = None

    context = {
        'product': product,
        'ratting': ratting,
        'rattingInt': ratting_int,
        'sale': sale,
        'new': new,
        'quantity': quantity,
        'sold': sold,
        'percent': percent,
        'tags_p': Tag.objects.filter(product=product),
        'accessories': accessories,
        'latest_products': latest_products,
        'menu_categories': menu_categories,
        'message_success': message_success
    }

    return render(request, 'ecommerce/product.html', context)


def quick_view(request, id_product="0"):
    # --------------------------- Product ---------------------------------
    if not Product.objects.filter(pk=id_product).exists():
        return HttpResponseRedirect('/e_commerce')
    product = Product.objects.get(pk=id_product)
    product.number_views += 1
    product.save()
    # ----------- Ratting
    ratting = Product.objects.filter(pk=id_product).aggregate(ratting=Avg('commerceratting__value'))['ratting']
    if ratting:
        ratting_int = int(ratting)
    else:
        ratting_int = 0
    # ----------- Sale
    sale = product.sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
    if sale.exists():
        sale = sale[0]
    else:
        sale = None
    if (timezone.localtime(timezone.now()).date() - product.date_add).days < 15:
        new = True
    else:
        new = False
    # ----------- Quantity
    quantity = product.stock_set.aggregate(Sum('quantity'))["quantity__sum"]
    if not quantity:
        quantity = 0
    first_quantity = product.stock_set.aggregate(Sum('first_quantity'))["first_quantity__sum"]
    if not first_quantity:
        first_quantity = 0
    if first_quantity == 0:
        percent = 0
    else:
        percent = (quantity * 100) / first_quantity
    sold = first_quantity - quantity

    context = {
        'product': product,
        'ratting': ratting,
        'rattingInt': ratting_int,
        'sale': sale,
        'new': new,
        'quantity': quantity,
        'sold': sold,
        'percent': percent,
        'tags_p': Tag.objects.filter(product=product),
    }
    return render(request, 'ecommerce/quickview.html', context)


def wish_list(request):
    user = request.user
    # -------------- Wish List
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('main_app:log_in'))
    wish_list_list = list()
    wish_list_result = WishList.objects.filter(user=user.profil)
    for el in wish_list_result:
        ob = dict()
        ob['el'] = el

        sale = el.product.sale_set.filter(date_end__gte=datetime.date.today())
        if sale.exists():
            ob['sale'] = sale[0]
        else:
            ob['sale'] = None

        if el.product.stock_set.exists():
            stock = el.product.stock_set.aggregate(quantity=Sum('quantity'))['quantity']
            if stock > 0:
                ob['stock'] = 'En Stock'
            else:
                ob['stock'] = "Rupture de Stock"
        else:
            ob['stock'] = 'Précommande'

        wish_list_list.append(ob)
        del ob
    context = {
        'wish_list_list': wish_list_list
    }
    return render(request, 'ecommerce/wish_list.html', context)


def compare(request):
    user = request.user
    # -------------- Compare
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('main_app:log_in'))
    compare_list = list()
    compare_list_result = Compare.objects.filter(user=user.profil)
    for el in compare_list_result:
        ob = dict()
        ob['el'] = el

        sale = el.product.sale_set.filter(date_end__gte=datetime.date.today())
        if sale.exists():
            ob['sale'] = sale[0]
        else:
            ob['sale'] = None

        if el.product.stock_set.exists():
            stock = el.product.stock_set.aggregate(quantity=Sum('quantity'))['quantity']
            if stock > 0:
                ob['stock'] = 'Rn Stock'
            else:
                ob['stock'] = "Ruptude de Stock"
        else:
            ob['stock'] = 'Précommande'

        if el.product.commerceratting_set.exists():
            ratting = el.product.commerceratting_set.aggregate(ratting=Avg('value'))['ratting']
            if ratting:
                ob['ratting'] = ratting
                ob['rattingInt'] = int(ratting)
            else:
                ob['ratting'] = 0
                ob['rattingInt'] = 0
        else:
            ob['ratting'] = 0
            ob['rattingInt'] = 0

        compare_list.append(ob)
        del ob
    count_span = 1
    if compare_list:
        count_span = len(compare_list) + 1
    context = {
        'compare_list': compare_list,
        'count_span': count_span
    }
    return render(request, 'ecommerce/compare.html', context)


def cart(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('main_app:log_in'))
    return render(request, 'ecommerce/cart.html')


def my_account(request):
    user = request.user

    # request.user
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('main_app:log_in'))
    # ----------------initialisation
    message_error = message_success = None
    newsletter_on = False
    mailing_object = None

    # ---------------- newsletter
    mailing = Mailing.objects.filter(email=user.email)
    if mailing.exists():
        mailing_object = mailing[0]
        if mailing_object.active:
            newsletter_on = True

    if request.method == "POST":
        # ---------------- get data
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if old_password and new_password and confirm_password:
            if old_password == user.password:
                if new_password == confirm_password:
                    user.password = new_password
                else:
                    message_error = "Confirmation Incorrect"
            else:
                message_error = "Password Incorrect"
        elif old_password or new_password or confirm_password:
            message_error = "Vous devez remplir tous les champs pour changer le mot de passe! Ou laissez les champs vides pour changer que les autres informations"
        if not message_error:
            first_name = request.POST.get('first_name')
            if first_name:
                user.first_name = str(first_name).capitalize()
            else:
                user.first_name = ""

            last_name = request.POST.get('last_name')
            if last_name:
                user.last_name = str(last_name).upper()
            else:
                user.last_name = ""

            email = request.POST.get('email')
            if email:
                if user.email != email:
                    if mailing_object:
                        mailing_object.delete()
                        Mailing.objects.get_or_create(email=email, active=False)
                        mailing_object = Mailing.objects.get(email=email)
                user.email = email
            else:
                user.email = ""
                if mailing_object:
                    mailing_object.delete()
                    mailing_object = None
            telephone = request.POST.get('telephone')
            if telephone:
                user.profil.tel = telephone
                user.profil.save()
            else:
                user.profil.tel = ""
                user.profil.save()

            newsletter = request.POST.get('newsletter')
            if newsletter == "1":
                if mailing_object:
                    mailing_object.active = True
                    mailing_object.save()
                else:
                    Mailing.objects.create(email=email, active=True)
                newsletter_on = True
            else:
                if mailing_object:
                    mailing_object.active = False
                    mailing_object.save()
                newsletter_on = False

            # Billing Address
            p_address = request.POST.get('P_address')
            p_company = request.POST.get('P_company')
            p_city = request.POST.get('P_city')
            p_postcode = request.POST.get('P_postcode')
            p_country = request.POST.get('P_country')
            p_region = request.POST.get('P_region')
            if BillingAddress.objects.filter(user=user.profil).exists():
                user.profil.billingaddress.address = p_address
                user.profil.billingaddress.city = p_city
                user.profil.billingaddress.post_code = p_postcode
                user.profil.billingaddress.country = p_country
                user.profil.billingaddress.region = p_region
            else:
                BillingAddress.objects.create(address=p_address, city=p_city, post_code=p_postcode,
                                              country=p_country, region=p_region, user=user.profil)

            if p_company:
                user.profil.billingaddress.company = p_company
            else:
                user.profil.billingaddress.company = ""

            # Shipping Address
            s_company = request.POST.get('S_company')
            s_address = request.POST.get('S_address')
            s_city = request.POST.get('S_city')
            s_postcode = request.POST.get('S_postcode')
            s_country = request.POST.get('S_country')
            s_region = request.POST.get('S_region')
            if ShippingAddress.objects.filter(user=user.profil).exists():
                user.profil.shippingaddress.address = s_address
                user.profil.shippingaddress.city = s_city
                user.profil.shippingaddress.post_code = s_postcode
                user.profil.shippingaddress.country = s_country
                user.profil.shippingaddress.region = s_region
            else:
                ShippingAddress.objects.create(address=s_address, city=s_city, post_code=s_postcode,
                                               country=s_country, region=s_region, user=user.profil)

            if s_company:
                user.profil.shippingaddress.company = s_company
            else:
                user.profil.shippingaddress.company = ""

            user.profil.shippingaddress.save()
            user.profil.billingaddress.save()
            user.profil.save()
            user.save()
            message_success = "Your account is up to date"

    context = {
        'newsletter_on': newsletter_on,
        'message_error': message_error,
        'message_success': message_success,
        'user': user
    }
    return render(request, 'ecommerce/my-account.html', context)


def contact_us(request):
    # ---------------- message
    message_success = None
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        Message.objects.create(name=name, email=email, message=message)
        message_success = "Votre message a été envoyé"

    context = {
        'message_success': message_success,
    }
    return render(request, 'ecommerce/contact-us.html', context)


def contact_supplier(request, id_product="None"):
    # user = request.user
    product = message_successs = None
    if id_product != "None":
        products_list = Product.objects.filter(pk=id_product)
        if products_list.exists():
            product = products_list[0]
    # ---------------- message
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        tel = request.POST.get("tel")
        quantity = request.POST.get('quantity')
        message = request.POST.get("message")
        supplier = product.supplier
        message = "Salut Mr {} {},<br/>Mr. {} vous contacte à propos de {} {} de {} code : #{} , Voici son message : \n{}" \
            .format(supplier.owner.user.last_name, supplier.owner.user.first_name, name, quantity, product.unit, product.name, product.pk,
                    message)
        MessageSupplier.objects.create(name=name, email=email, tel=tel, message=message, supplier=product.supplier)
        send_mail(
            'ESPR Order',
            message,
            'admin@socifly.com',
            [product.supplier.owner.user.email],
            fail_silently=False,
            html_message=message,
        )
        print('sent')
        message_successs = 'Votre message a été envoyé'
    context = {
        'product': product,
        'message_success': message_successs
    }
    return render(request, 'ecommerce/contact-supplier.html', context)


def faq(request):
    return render(request, 'ecommerce/faq.html')


def sitemap(request):
    context = {
        'brands': Brand.objects.all()
    }
    return render(request, 'ecommerce/sitemap.html', context)


def about_us(request):
    return render(request, 'ecommerce/about-us.html')


def checkout(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('main_app:log_in'))
    elif not ShippingAddress.objects.filter(user=user.profil).exists() or not BillingAddress.objects.filter(
            user=user.profil).exists():
        return HttpResponseRedirect(reverse('e_commerce:my_account'))
    elif not user.profil.shippingaddress.address or not user.profil.shippingaddress.city or not user.profil.shippingaddress.country or not user.profil.shippingaddress.post_code or not user.profil.shippingaddress.region or not user.profil.billingaddress.address or not user.profil.billingaddress.city or not user.profil.billingaddress.country or not user.profil.billingaddress.post_code or not user.profil.billingaddress.region:
        return HttpResponseRedirect(reverse('e_commerce:my_account'))
    if not request.method == 'POST':
        return render(request, 'ecommerce/checkout.html')
    comment = request.POST.get('comment', '')
    method_shipping = request.POST.get('shipping_method', 'Free Shipping')
    method_payment = request.POST.get('payment_method', 'Cash On Delivery')
    order = Order(user=user.profil, payment_method=method_payment, delivery_method=method_shipping, comment=comment,
                  amount=0)
    order.save()
    total_price_in_cart = 0
    cart_result = Cart.objects.filter(user=user.profil)
    for el in cart_result:
        sale = el.product.sale_set.filter(date_end__gte=datetime.date.today())
        if sale.exists():
            el.product.price = el.product.price - ((el.product.price * sale.all()[0].percentage) / 100)
        total = el.product.price * el.quantity
        order_line = OrderLine(quantity=el.quantity, total=total, order=order,
                               product=Product.objects.get(pk=el.product.pk), color=el.color)
        order_line.save()
        total_price_in_cart += total
    # --- Order
    if method_shipping == "Flat Shipping Rate":
        order.amount = (total_price_in_cart + 50)
    else:
        order.amount = total_price_in_cart
    order.save()

    if order.payment_method == "Paypal":
        request.session['order_id'] = order.pk
        return redirect(reverse('e_commerce:paypal_process'))
    order.status = "Processing"
    order.date_payment = datetime.date.today()
    Cart.objects.filter(user=user.profil).delete()
    order.save()
    message_success = "Votre Commande a été confirmée avec succés. Commande numéro #{}. Montant : {} Dh".format(
        order.pk, order.amount)
    message = "<p>Bonjour,</p><p>Votre Commande a été confirmée avec succés. Commande numéro <b>#{}</b>. Montant : <b>{} Dh</b></p>".format(
        order.pk, order.amount)
    send_mail(
        'Commande #{}'.format(order.pk),
        message,
        'admin@socifly.com',
        [order.user.user.email],
        fail_silently=False,
        html_message=message,
    )
    context = {
        'message_success': message_success,
        'order': order
    }
    return render(request, 'ecommerce/order-information.html', context)


def order_history(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('main_app:log_in'))
    # ---------------- orders
    orders = Order.objects.exclude(status__exact="Created").filter(user=request.user.profil)
    context = {
        'orders': orders
    }
    return render(request, 'ecommerce/order-history.html', context)


def order_information(request, id_order):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('main_app:log_in'))
    # ---------------- orders
    order_object = get_object_or_404(Order, pk=id_order)
    order_lines = order_object.orderline_set.all()
    total = order_object.orderline_set.all().aggregate(total=Sum('total'))['total']

    context = {
        'order': order_object,
        'order_lines': order_lines,
        'total': total
    }
    return render(request, 'ecommerce/order-information.html', context)


def suppliers_list(request):
    page = request.POST.get('page', 1)
    number_elements = request.POST.get('number_elements', 15)
    sort_by = request.POST.get("sort_by", "1")

    # ----------- Latest products
    latest_products = Product.objects.all().order_by('-date_add')[:15]
    latest_products = latest_products.values('id').annotate(ratting=Avg('commerceratting__value'))
    for el in latest_products:
        p = Product.objects.get(pk=el['id'])
        el['id'] = p

        if el['ratting']:
            el['rattingInt'] = int(el['ratting'])
        else:
            el['rattingInt'] = 0
            el['ratting'] = 0

        sale_l = p.sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
        if sale_l.exists():
            el['sale'] = sale_l[0]
        else:
            el['sale'] = None

    # ----------------- suppliers -----------------
    supplier_list = Shop.objects.filter(approved=True)
    if sort_by == "2":
        supplier_list = supplier_list.order_by("name")
    if sort_by == "3":
        supplier_list = supplier_list.order_by("-name")
    if sort_by == "8":
        supplier_list = supplier_list.order_by("date_creation")
    if sort_by == "9":
        supplier_list = supplier_list.order_by("-date_creation")

    supplier_list = supplier_list.values('id').annotate(ratting=Avg('product__commerceratting__value'), nbr=Count('product__id'))
    if sort_by == "4":
        supplier_list = supplier_list.order_by("ratting")
    if sort_by == "5":
        supplier_list = supplier_list.order_by("-ratting")
    if sort_by == "6":
        supplier_list = supplier_list.order_by("nbr")
    if sort_by == "7":
        supplier_list = supplier_list.order_by("-nbr")
    for el in supplier_list:
        el['id'] = Shop.objects.get(pk=el['id'])
        if el['ratting']:
            el['rattingInt'] = int(el['ratting'])
        else:
            el['rattingInt'] = 0
            el['ratting'] = 0
        if (timezone.localtime(timezone.now()).date() - el['id'].date_creation).days < 30:
            el['new'] = True
        else:
            el['new'] = False

    paginator = Paginator(supplier_list, number_elements)
    try:
        supplier_list = paginator.page(page)
    except PageNotAnInteger:
        supplier_list = paginator.page(1)
    except EmptyPage:
        supplier_list = paginator.page(paginator.num_pages)

    # range for display just 11 numbers
    index_page = supplier_list.number - 1
    max_index = len(paginator.page_range)
    start_index = index_page - 5 if index_page >= 4 else 0
    end_index = index_page + 5 if index_page <= max_index - 4 else max_index
    page_range = list(paginator.page_range)[start_index:end_index]

    context = {
        'suppliers': supplier_list,
        'latest_products': latest_products,

        'page_range': page_range,
        'sort_by': sort_by,
        'number_elements': number_elements,
    }
    return render(request, 'ecommerce/suppliers.html', context)


def display_supplier(request, id_supplier="0"):
    # ---------------- Featured brands
    brands = Brand.objects.exclude(image='').values('id').annotate(number=Count('product__id')).order_by('number')
    for el in brands:
        brand = Brand.objects.get(pk=el['id'])
        el['id'] = brand

    # ------------- supplier
    supplier = get_object_or_404(Shop, pk=id_supplier, approved=True)
    supplier.number_visitors = supplier.number_visitors + 1
    supplier.save()
    ratting = supplier.product_set.aggregate(rating=Avg('commerceratting__value'))['rating']
    if ratting:
        ratting_int = int(ratting)
    else:
        ratting_int = 0
    # ----------- Latest products
    latest_products = Product.objects.filter(supplier_id__exact=id_supplier, active=True, approved=True)
    latest_products = latest_products.values('id').annotate(ratting=Avg('commerceratting__value'), number=Sum('orderline__quantity')).order_by('number')[:15]
    for el in latest_products:
        p = get_object_or_404(Product, pk=el['id'])
        el['id'] = p

        if el['ratting']:
            el['rattingInt'] = int(el['ratting'])
        else:
            el['rattingInt'] = 0
            el['ratting'] = 0

        sale_l = p.sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
        if sale_l.exists():
            el['sale'] = sale_l[0]
        else:
            el['sale'] = None

    # Initialisation
    list_products = category = name = None
    products_results = Product.objects.filter(id__lte=-1)
    page_range = []
    found = True
    page = request.POST.get('page', 1)
    number_elements = request.POST.get('number_elements', 15)
    sort_by = request.POST.get("sort_by", "1")

    if id_supplier != "0":
        products_results = Product.objects.filter(supplier_id__exact=id_supplier)
    else:
        found = False

    if sort_by == "2":
        products_results = products_results.order_by(Lower("name"))
    elif sort_by == "3":
        products_results = products_results.order_by(Lower('name')).reverse()
    elif sort_by == "4":
        products_results = products_results.order_by('price')
    elif sort_by == "5":
        products_results = products_results.order_by('-price')
    elif sort_by == "8":
        products_results = products_results.order_by(Lower('brand__name'))
    elif sort_by == "9":
        products_results = products_results.order_by(Lower('brand__name')).reverse()
    elif sort_by == "10":
        products_results = products_results.order_by('-date_add')
    elif sort_by == "11":
        products_results = products_results.order_by('date_add')
    if products_results.exists():
        # select id, Avg(value) from product inner join commerce_ratting
        products_results = products_results.values('id').annotate(ratting=Avg('commerceratting__value'))
        if sort_by == "6":
            products_results = products_results.order_by('-ratting')
        if sort_by == "7":
            products_results = products_results.order_by('ratting')

        for el in products_results:
            product = Product.objects.get(pk=el['id'])
            el['id'] = product

            if el['ratting']:
                el['rattingInt'] = int(el['ratting'])
            else:
                el['rattingInt'] = 0
                el['ratting'] = 0

            if (timezone.localtime(timezone.now()).date() - product.date_add).days < 30:
                el['new'] = True
            else:
                el['new'] = False

            sale = product.sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
            if sale.exists():
                el['sale'] = sale[0]
            else:
                el['sale'] = None

            if product.stock_set.exists():
                el['quantity'] = product.stock_set.aggregate(quantity=Sum('quantity'))["quantity"]
                el['first_quantity'] = product.stock_set.aggregate(quantity=Sum('first_quantity'))["quantity"]
            else:
                el['quantity'] = 0
                el['first_quantity'] = 0

            images = CommerceImage.objects.filter(product=product)
            if images.exists():
                el['image'] = images[0].image
            else:
                el['image'] = None

            el['sold'] = el['first_quantity'] - el['quantity']

        paginator = Paginator(products_results, number_elements)
        try:
            list_products = paginator.page(page)
        except PageNotAnInteger:
            list_products = paginator.page(1)
        except EmptyPage:
            list_products = paginator.page(paginator.num_pages)

        # range for display just 11 numbers
        index_page = list_products.number - 1
        max_index = len(paginator.page_range)
        start_index = index_page - 5 if index_page >= 4 else 0
        end_index = index_page + 5 if index_page <= max_index - 4 else max_index
        page_range = list(paginator.page_range)[start_index:end_index]
    if found is False:
        list_products = None
    context = {
        'supplier': supplier,
        'results': list_products,
        'brands': brands,
        'name': name,
        'category': category,
        'latest_products': latest_products,
        'id_search': id_supplier,
        'ratting': ratting,
        'rattingInt': ratting_int,

        'categories_store': supplier.categories.all().order_by('name'),
        'page_range': page_range,
        'sort_by': sort_by,
        'number_elements': number_elements,
    }
    return render(request, 'ecommerce/supplier.html', context)


# ----------------- functions add remove update
def add_to_wish(request):
    product_id = request.GET.get('product', "None")
    message_error = ""
    number_products_in_wish_list = ""
    if request.user.is_authenticated:
        if product_id != "None":
            user = request.user
            products_wish = Product.objects.filter(pk=product_id)
            if products_wish.exists():
                if not WishList.objects.filter(user=user.profil, product=products_wish[0]).exists():
                    WishList.objects.create(user=user.profil, product=products_wish[0])
                    wish_list_result = WishList.objects.filter(user=user.profil)
                    number_products_in_wish_list = wish_list_result.count()
                else:
                    message_error = "Produit existe Déjà dans Votre liste des Souhaits"
            else:
                message_error = "Produit n'existe pas"
        else:
            message_error = "Erreur"
    else:
        message_error = "Vous devez se connecter!"
    data = {
        'message_error': message_error,
        'number_products_in_wish_list': number_products_in_wish_list
    }
    return JsonResponse(data)


def add_to_compare(request):
    product_id = request.GET.get('product', "None")
    message_error = ""
    number_products_in_compare = ""
    print('1')
    if request.user.is_authenticated:
        print('2')
        if product_id != "None":
            print('3')
            user = request.user
            products_compare = Product.objects.filter(pk=product_id)
            if products_compare.exists():
                print('4')
                if not Compare.objects.filter(user=user.profil, product=products_compare[0]).exists():
                    print('5')
                    Compare.objects.create(user=user.profil, product=products_compare[0])
                    compare_result = Compare.objects.filter(user=user.profil)
                    number_products_in_compare = compare_result.count()
                else:
                    message_error = "Produit existe Déjà dans Votre liste de Comparaison"
            else:
                message_error = "Produit n'existe pas"
        else:
            message_error = "Erreur"
    else:
        message_error = "Vous devez se connecter!"
    data = {
        'message_error': message_error,
        'number_products_in_compare': number_products_in_compare
    }
    return JsonResponse(data)


def add_to_cart(request):
    product_id = request.GET.get('product', "None")
    message_error = ""
    color_id = request.GET.get('option[231]', "None")
    quantity = request.GET.get('quantity', 1)
    price = total_price_in_cart = number_products_in_cart = message_warning = ""
    if request.user.is_authenticated:
        if product_id != "None":
            user = request.user
            products_wish = Product.objects.filter(pk=product_id)
            if products_wish.exists():
                if color_id == "None" or color_id == "0":
                    stock = Stock.objects.filter(product=products_wish[0])
                else:
                    stock = Stock.objects.filter(product=products_wish[0], color_id=color_id)
                    print('1')
                if stock.exists():
                    print('2')
                    cart_objects = Cart.objects.filter(user=user.profil, product=products_wish[0], color=stock[0].color)
                    if not cart_objects.exists():
                        print('3')
                        if int(quantity) < int(products_wish[0].quantity_min):
                            print('4')
                            quantity = products_wish[0].quantity_min
                            message_warning = "Quantité est {}".format(products_wish[0].quantity_min)
                        Cart.objects.create(user=user.profil, product=products_wish[0], color=stock[0].color,
                                            quantity=quantity)
                        print('5')
                        color_id = stock[0].color.pk
                        cart_result = Cart.objects.filter(user=user.profil)
                        number_products_in_cart = cart_result.count()
                        total_price_in_cart = 0
                        for el in cart_result:
                            stock = el.product.stock_set.filter(color=el.color)
                            if stock.exists():
                                el.product.price = el.product.price + stock.all()[0].price_sup
                            sale = el.product.sale_set.filter(date_end__gte=datetime.date.today())
                            if sale.exists():
                                el.product.price = el.product.price - (
                                        (el.product.price * sale.all()[0].percentage) / 100)
                            if el.product == products_wish[0]:
                                price = Decimal(el.product.price) * Decimal(quantity)
                            total_price_in_cart += (el.product.price * el.quantity)
                            print('hello')
                    else:
                        message_error = "Produit existe Déjà dans Votre liste de Comparaison"
                else:
                    message_error = "Produit en rupture stock"
            else:
                message_error = "Produit n'existe pas"
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error,
        'message_warning': message_warning,
        'total_price_in_cart': total_price_in_cart,
        'number_products_in_cart': number_products_in_cart,
        'price': price,
        'color_id': color_id,
        'quantity': quantity
    }
    return JsonResponse(data)


def remove_from_page_cart(request):
    if request.method == "POST":
        message_error = None
        id_cart = request.POST.get('cart')
        cart_object = Cart.objects.filter(pk=id_cart)
        if cart_object.exists():
            cart_object = cart_object[0]
            cart_object.delete()
        else:
            message_error = "Produit n'existe pas dans votre chariot"
        if message_error:
            context = {
                'message_error': message_error
            }
            return render(request, 'ecommerce/cart.html', context)

    next_page = request.POST.get('next', '/')
    return HttpResponseRedirect(next_page)


def remove_from_cart(request):
    message_error = ""
    total_price_in_cart = number_products_in_cart = ""
    user = request.user
    id_cart = request.GET.get('cart', "None")
    cart_object = Cart.objects.filter(pk=id_cart)
    if cart_object.exists():
        cart_object = cart_object[0]
        cart_object.delete()

        cart_result = Cart.objects.filter(user=user.profil)
        number_products_in_cart = cart_result.count()
        total_price_in_cart = 0
        for el in cart_result:
            stock = el.product.stock_set.filter(color=el.color)
            if stock.exists():
                el.product.price = el.product.price + stock.all()[0].price_sup
            sale = el.product.sale_set.filter(date_end__gte=datetime.date.today())
            if sale.exists():
                el.product.price = el.product.price - (
                        (el.product.price * sale.all()[0].percentage) / 100)
            total_price_in_cart += (el.product.price * el.quantity)
    else:
        message_error = "Produit n'existe pas dans votre chariot"
    data = {
        'message_error': message_error,
        'total_price_in_cart': total_price_in_cart,
        'number_products_in_cart': number_products_in_cart,
    }
    return JsonResponse(data)


def update_cart(request):
    if request.method == "POST":
        id_cart = request.POST.get('cart')
        cart_object = get_object_or_404(Cart, pk=id_cart)
        quantity = request.POST.get('quantity', 1)
        if int(quantity) < cart_object.product.quantity_min:
            message_error = "Votre commande ne respecte pas la quantité minimal d'achat pour ce produit: {} {}".format(cart_object.product.quantity_min, cart_object.product.unit)
            context = {
                'message_error': message_error
            }
            return render(request, 'ecommerce/cart.html', context)
        cart_object.quantity = quantity
        cart_object.save()
    next_page = request.POST.get('next', '/')
    return HttpResponseRedirect(next_page)


def update_color_cart(request):
    if request.method == "POST":
        message_error = None
        id_cart = request.POST.get('cart')
        id_color = request.POST.get('option[231]')
        cart_object = Cart.objects.filter(pk=id_cart)
        if cart_object.exists():
            cart_object = cart_object[0]
            cart_object.color = Color.objects.get(pk=id_color)
            cart_object.save()
        else:
            message_error = "Produit n'existe pas"
        if message_error:
            context = {
                'message_error': message_error
            }
            return render(request, 'ecommerce/cart.html', context)
    next_page = request.POST.get('next', '/')
    return HttpResponseRedirect(next_page)


def add_from_wish(request):
    if request.method == "POST":
        message_error = None
        user = request.user
        if not user.is_authenticated:
            return HttpResponseRedirect(reverse('main_app:log_in'))
        id_product = request.POST.get('product')
        products_wish = Product.objects.filter(pk=id_product, active=True, approved=True)
        if products_wish.exists():
            wish_object = WishList.objects.filter(user=user.profil, product=products_wish[0])
            if wish_object.exists():
                stock = Stock.objects.filter(product=products_wish[0])
                if stock.exists():
                    if not Cart.objects.filter(user=user.profil, product=products_wish[0],
                                               color=stock[0].color).exists():
                        Cart.objects.create(user=user.profil, product=products_wish[0], color=stock[0].color)
                    else:
                        message_error = "Produit existe déjà dans votre chariot"
                else:
                    message_error = "Produit en rupture de stock"
            else:
                message_error = "Produit n'existe pas dans votre List des Souhaits"
        else:
            message_error = "Produit n'existe pas"
        if message_error:
            # -------------- Wish List
            wish_list_list = list()
            wish_list_result = WishList.objects.filter(user=user.profil)
            for el in wish_list_result:
                ob = dict()
                ob['el'] = el

                sale = el.product.sale_set.filter(date_end__gte=datetime.date.today())
                if sale.exists():
                    ob['sale'] = sale[0]
                else:
                    ob['sale'] = None

                if el.product.stock_set.exists():
                    stock = el.product.stock_set.aggregate(quantity=Sum('quantity'))['quantity']
                    if stock > 0:
                        ob['stock'] = 'En Stock'
                    else:
                        ob['stock'] = "Rupture de Stock"
                else:
                    ob['stock'] = 'Precommande'

                wish_list_list.append(ob)
                del ob
            context = {
                'wish_list_list': wish_list_list,
                'message_error': message_error
            }
            return render(request, 'ecommerce/wish_list.html', context)
    return HttpResponseRedirect(reverse('e_commerce:wish_list'))


def remove_from_wish(request):
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            return HttpResponseRedirect(reverse('main_app:log_in'))
        id_product = request.POST.get('product')
        products_wish = get_object_or_404(Product, pk=id_product)
        wish_object = get_object_or_404(WishList, user=user.profil, product=products_wish)
        wish_object.delete()
    return HttpResponseRedirect(reverse('e_commerce:wish_list'))


def add_from_compare(request):
    if request.method == "POST":
        message_error = None
        user = request.user
        id_product = request.POST.get('product')
        products_compare = Product.objects.filter(pk=id_product)
        if products_compare.exists():
            compare_object = Compare.objects.filter(user=user.profil, product=products_compare[0])
            if compare_object.exists():
                stock = Stock.objects.filter(product=products_compare[0])
                if stock.exists():
                    if not Cart.objects.filter(user=user.profil, product=products_compare[0],
                                               color=stock[0].color).exists():
                        Cart.objects.create(user=user.profil, product=products_compare[0], color=stock[0].color)
                    else:
                        message_error = "Produit existe déjà dans votre chariot"
                else:
                    message_error = "Produit en rupture de stock"
            else:
                message_error = "Produit n'existe pas dans votre liste de comparaison"
        else:
            message_error = "Produit n'existe pas"
        if message_error:
            # -------------- Compare
            if user.is_authenticated:
                compare_list = list()
                compare_list_result = Compare.objects.filter(user=user.profil)[:4]
                for el in compare_list_result:
                    ob = dict()
                    ob['el'] = el

                    sale = el.product.sale_set.filter(date_end__gte=datetime.date.today())
                    if sale.exists():
                        ob['sale'] = sale[0]
                    else:
                        ob['sale'] = None

                    if el.product.stock_set.exists():
                        stock = el.product.stock_set.aggregate(quantity=Sum('quantity'))['quantity']
                        if stock > 0:
                            ob['stock'] = 'In Stock'
                        else:
                            ob['stock'] = "Out of Stock"
                    else:
                        ob['stock'] = 'Pre-Order'

                    if el.product.commerceratting_set.exists():
                        ratting = el.product.commerceratting_set.aggregate(ratting=Avg('value'))['ratting']
                        if ratting:
                            ob['ratting'] = ratting
                            ob['rattingInt'] = int(ratting)
                        else:
                            ob['ratting'] = 0
                            ob['rattingInt'] = 0
                    else:
                        ob['ratting'] = 0
                        ob['rattingInt'] = 0

                    compare_list.append(ob)
                    del ob
            else:
                return HttpResponseRedirect('/e_commerce')
            count_span = 1
            if compare_list:
                count_span = len(compare_list) + 1
            context = {
                'compare_list': compare_list,
                'count_span': count_span,
                'message_error': message_error
            }
            return render(request, 'ecommerce/compare.html', context)

    return HttpResponseRedirect(reverse('e_commerce:wish_list'))


def remove_from_compare(request):
    if request.method == "POST":
        user = request.user
        id_product = request.POST.get('product')
        products_compare = Product.objects.filter(pk=id_product)
        if products_compare.exists():
            compare_object = Compare.objects.filter(user=user.profil, product=products_compare[0])
            if compare_object.exists():
                compare_object = compare_object[0]
                compare_object.delete()
    return HttpResponseRedirect(reverse('e_commerce:compare'))


# ------------------- Methods
def all_categories():
    return CommerceCategory.objects.all()


def all_tags():
    return Tag.objects.all()


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
    return {'cart': cart_result, 'number_products_in_cart': number_products_in_cart,
            'total_price_in_cart': total_price_in_cart}


def my_featured_sale():
    hot_categories = list()
    featured_sale = Sale.objects.filter(date_end__gte=datetime.date.today(), product__active=True, product__approved=True).values(
        'product__cat__category_two__category_one__category').annotate(Max('percentage')).order_by('-percentage__max')[:6]
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
    return {'hot_categories': hot_categories, 'featured_sale': featured_sale}


def test(request, id_request):
    return HttpResponse("hi {}".format(id_request))


def paypal_process(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('main_app:log_in'))
    order_id = request.session.get('order_id', "")
    order = get_object_or_404(Order, id=order_id)
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": str(order.amount),
        "item_name": "Commande #{}".format(order.id),
        "invoice": str(order.id),
        "currency_code": "USD",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri(reverse('e_commerce:paypal_done')),
        "cancel_return": request.build_absolute_uri(reverse('e_commerce:paypal_cancel')),
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {
        "form": form,
        'order': order
    }
    return render(request, "ecommerce/paypal_process.html", context)


@csrf_exempt
def paypal_done(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('main_app:log_in'))
    if 'order_id' not in request.session:
        return HttpResponseRedirect(reverse('e_commerce:index'))
    Cart.objects.filter(user=user.profil).delete()
    message_success = "Votre Paiement a été effectué. plus de détails vous serons communiquer très prochainement."
    order = get_object_or_404(Order, pk=request.session['order_id'])
    del request.session['order_id']
    context = {
        'message_success': message_success,
        'order': order
    }
    return render(request, 'ecommerce/order-history.html', context)


@csrf_exempt
def paypal_cancel(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('main_app:log_in'))
    message_error = None
    if 'order_id' in request.session:
        message_error = "Votre Paiement a été annulé."
    context = {
        'message_error': message_error
    }
    return render(request, 'ecommerce/checkout.html', context)


#-------- issa
def create_store(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('main_app:log_in'))
    user = request.user.profil
    #if user.id in Shop.objects.values_list('owner', flat=True):
    #    return redirect('e_commerce:my_account')
    form = StoreForm()

    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            store = Shop.objects.create(
                name=cd['name'],
                image_profile=cd['image_profile'],
                image_cover=cd['image_cover'],
                address=cd['address'],
                tel=cd['number_contact'],
                description=cd['description'],
                owner=user
            )
            cats = request.POST.getlist('cats', None)
            for cat in cats:
                store.categories.add(cat)
            store.save()
            return redirect('e_commerce:my_account')
    context = {
        'form': form,
        'cats': CommerceSCategoryOne.objects.all().order_by('name')
    }
    return render(request, 'ecommerce/create-store.html', context)


# ## ADD PRODUCT VIEW ## #
def add_product(request):
    form = AddProductForm()
    if request.user.is_authenticated:
        user = request.user.profil
        product_id = request.session.get('product_id', None)
        print(product_id)
        if request.method == 'POST':
            if product_id is not None:
                form = AddProductForm(request.POST, request.FILES)
                if form.is_valid():
                    cd = form.cleaned_data
                    product = get_object_or_404(Product, id=product_id)
                    product.name = cd['name']
                    product.image = cd['image']
                    product.price = cd['price']
                    product.cat = cd['category']
                    product.brand = cd['brand']
                    product.quantity_min = cd['min_quantity']
                    product.unit = cd['unit']
                    professional = cd['professional']
                    if professional == 'yes':
                        product.is_pro = True
                    else:
                        product.is_pro = False
                    old_price = cd['old_price']
                    if old_price:
                        product.old_price = old_price
                    price_from = request.POST.get('price_from')
                    if price_from == 'yes':
                        product.price_from = True
                    product.packaging_detail = cd['packaging']
                    product.delivery_time = cd['delivery']
                    product.content = cd['description']
                    product.active = True
                    tags = request.POST.getlist('tags')
                    for t in tags:
                        product.tags.add(get_object_or_404(Tag, id=t))
                    product.save()
                    del request.session['product_id']
                    request.session['message_warning'] = "Votre Produit sera approuvé par des administrateurs"
                    print(request.session['message_warning'])
                    return redirect('e_commerce:your_products')
        if product_id is None:
            store = get_object_or_404(Shop, owner=user)
            request.session['product_id'] = Product.objects.create(name="Session product", supplier=store).id
        elif Product.objects.filter(id=product_id).exists():
            product = Product.objects.get(id=product_id)
            product.delete()
            store = Shop.objects.get(owner=user)
            request.session['product_id'] = Product.objects.create(name="Session product", supplier=store).id

        context = {
            'form': form,
            'tags_form': Tag.objects.all().order_by('name'),
            'stock_form': AddProductStockForm,
            'specification_form': AddProductSpecificationForm,
            'detail_form': AddProductDetailForm
        }

        return render(request, 'ecommerce/add_product.html', context)

    return redirect('e_commerce:index')


def product_cancel(request):
    if request.user.is_authenticated:
        user = request.user.profil
        product_id = request.session.get('product_id', None)
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner != user:
            return redirect('e_commerce:my_account')
        CommerceImage.objects.filter(product=product).delete()
        product.delete()
        del request.session['product_id']
        return redirect('e_commerce:products')


@require_POST
def product_upload_image(request):
    if request.user.is_authenticated:
        user = request.user.profil
        product_id = request.session.get('product_id', None)
        product = Product.objects.get(id=product_id)
        if product.supplier.owner != user:
            return redirect('e_commerce:add_product')

        # GET Product IMAGES FROM POST
        form = ProductImageImport(request.POST, request.FILES)
        if form.is_valid():
            image = form.save()
            image.product = product
            image.save()
            data = {
                'is_valid': True,
                'name': image.image.name,
                'url': image.image.url,
                'id': image.id
            }
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


def product_delete_image(request, image_id):
    if request.user.is_authenticated:
        user = request.user.profil
        product_id = request.session.get('product_id', None)
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner != user:
            return redirect('e_commerce:add_product')
        image = get_object_or_404(CommerceImage, id=image_id)
        image.delete()
        data = {
            'message': 'success',
            'tr': '#tr' + str(image_id)
        }
        return JsonResponse(data)

    return redirect('e_commerce:index')


def product_add_stock(request):
    if request.user.is_authenticated:
        user = request.user.profil
        product_id = request.session.get('product_id', None)
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner == user:
            quantity = request.GET.get('quantity', None)
            price_sup = request.GET.get('price_sup', None)
            color = request.GET.get('color', None)
            valid = True
            if (quantity is None) or (quantity == ''):
                valid = False
            if valid is False:
                data = {'valid': False}
            else:
                color_stock = Color.objects.create(name='color '+color, code_hex=color)
                Stock.objects.create(quantity=quantity, price_sup=price_sup, color=color_stock, product=product, first_quantity=quantity)
                data = {'valid': True}
            return JsonResponse(data)
    return redirect('e_commerce:add_product')


def product_add_specification(request):
    if request.user.is_authenticated:
        user = request.user.profil
        product_id = request.session.get('product_id', None)
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner == user:
            name = request.GET.get('name', None)
            content = request.GET.get('content', None)
            valid = True
            if (name is None) or (name == ''):
                valid = False
            if (content is None) or (content == ''):
                valid = False
            if valid is False:
                data = {'valid': False}
            else:
                Specification.objects.create(name=name, value=content, product=product)
                data = {'valid': True}
            return JsonResponse(data)
    return redirect('e_commerce:add_product')


def product_add_detail(request):
    if request.user.is_authenticated:
        user = request.user.profil
        product_id = request.session.get('product_id', None)
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner == user:
            name = request.GET.get('name', None)
            value = request.GET.get('value', None)
            valid = True
            if (name is None) or (name == ''):
                valid = False
            if (value is None) or (value == ''):
                valid = False
            if valid is False:
                data = {'valid': False}
            else:
                CommerceInformation.objects.create(name=name, value=value, product=product)
                data = {'valid': True}
            return JsonResponse(data)
    return redirect('e_commerce:add_product')


def product_add_tag(request):
    if request.user.is_authenticated:
        user = request.user.profil
        product_id = request.session.get('product_id', None)
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner == user:
            name = request.GET.get('name', None)
            valid = True
            if (name is None) or (name == ''):
                valid = False
            if valid is False:
                data = {'valid': False}
            else:
                tag = Tag.objects.create(name=name)
                data = {
                    'valid': True,
                    'id': tag.id,
                    'value': tag.name
                }
            return JsonResponse(data)
    return redirect('e_commerce:add_product')


# ## UPDATE PRODUCT VIEW ## #
def update_product(request, product_id):
    if request.user.is_authenticated:
        user = request.user.profil
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner != user:
            return redirect('e_commerce:my-account')
        if request.method == 'POST':
            if product_id is not None:
                form = UpdateProductForm(request.POST, request.FILES)
                if form.is_valid():
                    cd = form.cleaned_data
                    product.name = cd['name']
                    img = cd['image']
                    if img:
                        product.image = cd['image']
                    product.price = cd['price']
                    product.cat = cd['category']
                    product.brand = cd['brand']
                    product.quantity_min = cd['min_quantity']
                    product.unit = cd['unit']
                    professional = cd['professional']
                    if professional == 'yes':
                        product.is_pro = True
                    else:
                        product.is_pro = False
                    old_price = cd['old_price']
                    if old_price:
                        product.old_price = old_price
                    price_from = request.POST.get('price_from')
                    if price_from == 'yes':
                        product.price_from = True
                    product.packaging_detail = cd['packaging']
                    product.delivery_time = cd['delivery']
                    product.content = cd['description']
                    product.active = True
                    tags = request.POST.getlist('tags')
                    for t in tags:
                        product.tags.add(get_object_or_404(Tag, id=t))
                    product.save()
                    return redirect('e_commerce:your_products')

        else:
            form = UpdateProductForm(initial={
                'name': product.name,
                'price': product.price,
                'category': product.cat,
                'brand': product.brand,
                'min_quantity': product.quantity_min,
                'unit': product.unit,
                'old_price': product.old_price,
                'packaging': product.packaging_detail,
                'delivery': product.delivery_time,
                'description': product.content
            })

        context = {
            'form': form,
            'tags_form': Tag.objects.all().order_by('name'),
            'stock_form': AddProductStockForm,
            'specification_form': AddProductSpecificationForm,
            'detail_form': AddProductDetailForm,
            'tags': product.tags.all(),
            'pro': product.is_pro,
            'price_cat': product.price_from,
            'stocks': product.stock_set.all(),
            'details': product.commerceinformation_set.all(),
            'specifications': product.specification_set.all(),
            'images': product.commerceimage_set.all(),
            'product': product
        }

        return render(request, 'ecommerce/update_product.html', context)

    return redirect('e_commerce:index')


@require_POST
def up_product_upload_image(request, product_id):
    print(product_id)
    if request.user.is_authenticated:
        user = request.user.profil
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner != user:
            return redirect('e_commerce:my-account')

        # GET Product IMAGES FROM POST
        form = ProductImageImport(request.POST, request.FILES)
        if form.is_valid():
            image = form.save()
            image.product = product
            image.save()
            data = {
                'is_valid': True,
                'name': image.image.name,
                'url': image.image.url,
                'id': image.id
            }
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


def up_product_delete_image(request, product_id, image_id):
    if request.user.is_authenticated:
        user = request.user.profil
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner != user:
            return redirect('e_commerce:my-account')
        image = get_object_or_404(CommerceImage, id=image_id)
        image.delete()
        data = {
            'message': 'success',
            'tr': '#tr' + str(image_id)
        }
        return JsonResponse(data)

    return redirect('e_commerce:index')


def up_product_add_stock(request, product_id):
    if request.user.is_authenticated:
        user = request.user.profil
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner == user:
            quantity = request.GET.get('quantity', None)
            price_sup = request.GET.get('price_sup', None)
            color = request.GET.get('color', None)
            valid = True
            if (quantity is None) or (quantity == ''):
                valid = False
            if valid is False:
                data = {'valid': False}
            else:
                color_stock = Color.objects.create(name='color '+color, code_hex=color)
                s = Stock.objects.create(quantity=quantity, price_sup=price_sup, color=color_stock, product=product, first_quantity=quantity)
                data = {
                    'valid': True,
                    'message': 'Stock ' + str(s.id) + ', quantité: ' + str(s.quantity) + ', couleur: ' + color
                }
            return JsonResponse(data)
    return redirect('e_commerce:add_product')


def up_product_add_specification(request, product_id):
    if request.user.is_authenticated:
        user = request.user.profil
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner == user:
            name = request.GET.get('name', None)
            content = request.GET.get('content', None)
            valid = True
            if (name is None) or (name == ''):
                valid = False
            if (content is None) or (content == ''):
                valid = False
            if valid is False:
                data = {'valid': False}
            else:
                s = Specification.objects.create(name=name, value=content, product=product)
                data = {
                    'valid': True,
                    'message': 'Spécification ' + str(s.id) + ', nom: ' + str(s.name) + ', contenu: ' + content
                }
            return JsonResponse(data)
    return redirect('e_commerce:add_product')


def up_product_add_detail(request, product_id):
    if request.user.is_authenticated:
        user = request.user.profil
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner == user:
            name = request.GET.get('name', None)
            value = request.GET.get('value', None)
            valid = True
            if (name is None) or (name == ''):
                valid = False
            if (value is None) or (value == ''):
                valid = False
            if valid is False:
                data = {'valid': False}
            else:
                c = CommerceInformation.objects.create(name=name, value=value, product=product)
                data = {
                    'valid': True,
                    'message': 'Détail ' + str(c.id) + ', nom: ' + str(c.name) + ', valeur: ' + c.value
                }
            return JsonResponse(data)
    return redirect('e_commerce:add_product')


def up_product_add_tag(request, product_id):
    if request.user.is_authenticated:
        user = request.user.profil
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner == user:
            name = request.GET.get('name', None)
            valid = True
            if (name is None) or (name == ''):
                valid = False
            if valid is False:
                data = {'valid': False}
            else:
                tag = Tag.objects.create(name=name)
                data = {
                    'valid': True,
                    'id': tag.id,
                    'value': tag.name
                }
            return JsonResponse(data)
    return redirect('e_commerce:add_product')


def up_product_delete_spec(request, product_id, spec_id):
    if request.user.is_authenticated:
        user = request.user.profil
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner != user:
            return redirect('e_commerce:my-account')
        s = get_object_or_404(Specification, id=spec_id)
        s.delete()
        data = {
            'message': 'success',
            'tr': '#tr_spec' + str(spec_id)
        }
        return JsonResponse(data)

    return redirect('e_commerce:index')


def up_product_delete_stock(request, product_id, stock_id):
    if request.user.is_authenticated:
        user = request.user.profil
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner != user:
            return redirect('e_commerce:my-account')
        s = get_object_or_404(Stock, id=stock_id)
        s.delete()
        data = {
            'message': 'success',
            'tr': '#tr_stock' + str(stock_id)
        }
        return JsonResponse(data)

    return redirect('e_commerce:index')


def up_product_delete_detail(request, product_id, detail_id):
    if request.user.is_authenticated:
        user = request.user.profil
        product = get_object_or_404(Product, id=product_id)
        if product.supplier.owner != user:
            return redirect('e_commerce:my-account')
        detail = get_object_or_404(CommerceInformation, id=detail_id)
        detail.delete()
        data = {
            'message': 'success',
            'tr': '#tr_detail' + str(detail_id)
        }
        return JsonResponse(data)

    return redirect('e_commerce:index')
