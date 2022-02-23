import django
from django.forms import DecimalField
from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Func, Value, ExpressionWrapper
from django.db.models.functions import Concat
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
from django.db import transaction
from store.models import OrderItem, Product, Customer, Collection, Order

# can add transaction wrapper
# @transaction.atomic()
def say_hello(request):
    # objects is a MODEL MANAGER that gives us an interface to work with database
    try:
        query_set = Product.objects.all()
        for product in query_set:
            print(product)
    except ObjectDoesNotExist:
        pass
    # inventory<10 OR price<20
    query_set = Product.objects.filter(
        Q(inventory__lt=10) | Q(unit_price__lt=20))

    # referencing between fields like inventory=unit_price
    query_set = Product.objects.filter(inventory=F('unit_price'))

    # sorting
    # sort by unit_price in ascending and title in descending
    query_set = Product.objects.order_by('unit_price', '-title')
    # reverse
    query_set = Product.objects.order_by('unit_price', '-title').reverse()
    # get single object
    product = Product.objects.order_by('unit_price')[0]
    product = Product.objects.earliest('unit_price')
    # get latest
    product = Product.objects.latest('unit_price')

    # limit and offset
    # LIMIT in SQL
    query_set = Product.objects.all()[:5]
    # OFFSET with LIMIT in SQL
    query_set = Product.objects.all()[5:10]

    # get all ordered product's title in sorted order; SELECT -> values
    queryset = Product.objects.filter(id__in=OrderItem.objects.values(
        'product_id').distinct()).order_by('title')

    # get related table
    # select related(1)
    # prefetch_related(n)
    queryset = Product.objects.select_related('collection').all()
    queryset = Product.objects.prefetch_related('promotions').all()

    # aggregate
    result = Product.objects.aggregate(
        count=Count('id'), min_price=Min('unit_price'))

    # database functions
    queryset = Customer.objects.annotate(full_name=Func(
        F('first_name'), Value(' '), F('last_name'), function='CONCAT'))
    queryset = Customer.objects.annotate(
        full_name=Concat('first_name', Value(' '), 'last_name'))

    # Expression Wrappers
    discounted_price = ExpressionWrapper(
        F('unit_price')*0.8, output_field=DecimalField())
    queryset = Product.objects.annotate(discounted_price=discounted_price)

    # insert
    collection = Collection()
    collection.title = 'Video games'
    collection.featured_product = Product(pk=1)
    collection.save()
    # same
    # collection = collection.objects.create(name='Video games', featured_product_id=1)

    # update
    # remeber to read before updating else might set unmentioned fields to none
    collection = Collection.objects.get(pk=11)
    collection.featured_product = None
    collection.save()
    # if want to reduce the read call
    Collection.objects.filter(pk=1).update(featured_product=None)

    # Delete
    # single
    collection = Collection.objects.get(pk=11)
    collection.delete()
    # multiple
    Collection.objects.filter(id__gt=5).delete()

    # atomic transaction
    with transaction.atomic():
        order = Order()
        order.customer_id = 1
        order.save()
        item = OrderItem()
        item.order = order
        item.product_id = 1
        item.quantity = 1
        item.unit_price = 10
        item.save()

    # raw sql
    queryset = Product.objects.raw('SELECT * FROM store_product')
    


    # return HttpResponse('Hello world')
    return render(request, 'hello.html', {'name': 'test'})
