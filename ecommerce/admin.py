from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


class CateGoryOneInline(admin.StackedInline):
    model = CommerceSCategoryOne
    extra = 3


class CategoryAdmin(admin.ModelAdmin):
    inlines = [CateGoryOneInline]
    readonly_fields = ["display_image_", ]
    search_fields = ['name']
    list_display = ('id', 'name', 'display_image')
    list_per_page = 100

    @staticmethod
    def display_image_(obj):
        if obj.image:
            return mark_safe('<img src="{url}" width="{width}" height={height} style="max-width: 600px; max-height: 300px" />'.format(
                url=obj.image.url,
                width=obj.image.width,
                height=obj.image.height,
                )
            )

    @staticmethod
    def display_image(obj):
        if obj.image:
            return mark_safe('<img src="{url}" width="100px" height="50px" />'.format(url=obj.image.url))


class CateGoryTwoInline(admin.StackedInline):
    model = CommerceSCategoryTwo
    extra = 3


class CategoryOneAdmin(admin.ModelAdmin):
    inlines = [CateGoryTwoInline]
    search_fields = ['name']


class CateGorySInline(admin.StackedInline):
    model = CommerceSCategory
    extra = 3


class CategoryTwoAdmin(admin.ModelAdmin):
    inlines = [CateGorySInline]
    search_fields = ['name']


class CategorySAdmin(admin.ModelAdmin):
    search_fields = ['name']


class BrandAdmin(admin.ModelAdmin):
    readonly_fields = ["display_image_", ]
    search_fields = ['name']
    list_display = ('id', 'name', 'display_image')

    @staticmethod
    def display_image_(obj):
        if obj.image:
            return mark_safe('<img src="{url}" width="{width}" height={height} style="max-width: 600px; max-height: 300px" />'.format(
                url=obj.image.url,
                width=obj.image.width,
                height=obj.image.height,
                )
            )

    @staticmethod
    def display_image(obj):
        if obj.image:
            return mark_safe('<img src="{url}" width="100px" height="50px" />'.format(
                url=obj.image.url
                )
            )


class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']


class ImageInline(admin.TabularInline):
    model = CommerceImage
    extra = 1


class SaleInline(admin.TabularInline):
    model = Sale
    extra = 1


class StockInline(admin.TabularInline):
    model = Stock
    extra = 1


class InformationInline(admin.TabularInline):
    model = CommerceInformation
    extra = 1


class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = [StockInline, SaleInline, ImageInline, InformationInline, SpecificationInline]
    readonly_fields = ["display_image_", ]
    search_fields = ['name', 'price']
    list_display = ('id', 'display_image', 'name', 'price', 'unit', 'supplier', 'cat', 'active', 'approved')
    list_filter = ('active', 'approved', 'supplier', 'brand', 'cat')

    @staticmethod
    def display_image_(obj):
        if obj.image:
            return mark_safe('<img src="{url}" width="{width}" height={height} style="max-width: 600px; max-height: 600px" />'.format(
                url=obj.image.url,
                width=obj.image.width,
                height=obj.image.height,
                )
            )

    @staticmethod
    def display_image(obj):
        if obj.image:
            return mark_safe('<img src="{url}" width="60px" height="60px" />'.format(
                url=obj.image.url
                )
            )


class InformationAdmin(admin.ModelAdmin):
    search_fields = ['name', 'value']
    list_display = ('id', 'name', 'value', 'product')
    list_filter = ('product',)


class ImageAdmin(admin.ModelAdmin):
    readonly_fields = ["display_image_"]
    list_display = ('id', 'display_image', 'product')
    list_filter = ('product',)

    @staticmethod
    def display_image_(obj):
        if obj.image:
            return mark_safe('<img src="{url}" width="{width}" height={height} style="max-width: 600px; max-height: 600px" />'.format(
                url=obj.image.url,
                width=obj.image.width,
                height=obj.image.height,
                )
            )

    @staticmethod
    def display_image(obj):
        if obj.image:
            return mark_safe('<img src="{url}" width="60px" height="60px" />'.format(
                url=obj.image.url
                )
            )


class RatingAdmin(admin.ModelAdmin):
    search_fields = ['name', 'value']
    list_display = ('id', 'name', 'value', 'comment', 'product')
    list_filter = ('product',)


class ColorAdmin(admin.ModelAdmin):
    readonly_fields = ["display_color_"]
    search_fields = ['name']
    list_display = ('id', 'name', 'code_hex', 'display_color')
    list_per_page = 100

    @staticmethod
    def display_color_(obj):
        if obj.code_hex:
            return mark_safe(
                '<div style="background-color: {url}; width:30px; height:30px; border: 1px black solid;"> </div>'.format(
                    url=obj.code_hex
                )
            )

    @staticmethod
    def display_color(obj):
        if obj.code_hex:
            return mark_safe(
                '<div style="background-color: {url}; width:30px; height:30px; border: 1px black solid;"> </div>'.format(
                    url=obj.code_hex
                )
            )
        else:
            return '-'


class SpecificationAdmin(admin.ModelAdmin):
    search_fields = ['name', 'value']
    list_display = ('id', 'name', 'value', 'product')
    list_filter = ('product',)


class SaleAdmin(admin.ModelAdmin):
    search_fields = ['percentage']
    list_display = ('id', 'product', 'percentage', 'date_end', 'is_daily')
    list_filter = ('product', 'percentage')


class StockAdmin(admin.ModelAdmin):
    search_fields = ['quantity']
    list_display = ('id', 'product', 'color', 'quantity', 'price_sup')
    list_filter = ('color', 'product')


class WishListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product')
    list_filter = ('product', )


class CompareAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product')
    list_filter = ('product', )


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity')
    list_filter = ('product', )


class OrderAdmin(admin.ModelAdmin):
    search_fields = ['amount']
    list_display = ('id', 'user', 'amount', 'status', 'payment_method', 'delivery_method', 'track_number')
    list_filter = ('status', 'payment_method', 'delivery_method')


class OrderLineAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'color', 'quantity', 'total')
    list_filter = ('color', 'product')
    search_fields = ['total']


class SlideAdmin(admin.ModelAdmin):
    readonly_fields = ["display_image_"]
    list_display = ('id', 'display_image', 'product', 'active')
    list_filter = ('product', 'active')

    @staticmethod
    def display_image_(obj):
        if obj.image:
            return mark_safe('<img src="{url}" width="{width}" height={height} style="max-width: 800px; max-height: 400px" />'.format(
                url=obj.image.url,
                width=obj.image.width,
                height=obj.image.height,
                )
            )

    @staticmethod
    def display_image(obj):
        if obj.image:
            return mark_safe('<img src="{url}" width="120px" height="60px" />'.format(
                url=obj.image.url
                )
            )


class ShippingAddressAdmin(admin.ModelAdmin):
    search_fields = ['city', 'post_code', 'company', 'address', 'country', 'region']
    list_display = ('id', 'address', 'country', 'city', 'post_code', 'region', 'company')
    list_filter = ('country', 'city')


class BillingAddressAdmin(admin.ModelAdmin):
    search_fields = ['city', 'post_code', 'company', 'address', 'country', 'region']
    list_display = ('id', 'address', 'country', 'city', 'post_code', 'region', 'company')
    list_filter = ('country', 'city')


class MailingAdmin(admin.ModelAdmin):
    search_fields = ['email', ]
    list_display = ('id', 'email', 'active', 'date_add')
    list_filter = ('active', )


class MessageAdmin(admin.ModelAdmin):
    search_fields = ['email', 'name', 'message']
    list_display = ('id', 'name', 'email', 'message_', 'date_add')
    list_filter = ('date_add', )

    @staticmethod
    def message_(obj):
        if obj.message:
            return mark_safe('<p>{msg}</p>'.format(msg=obj.message))


class MessageSupplierAdmin(admin.ModelAdmin):
    search_fields = ['email', 'name', 'message', 'tel']
    list_display = ('id', 'name', 'email', 'message_', 'date_add')
    list_filter = ('date_add', )

    @staticmethod
    def message_(obj):
        if obj.message:
            return mark_safe('<p>{msg}</p>'.format(msg=obj.message))


class ShopAdmin(admin.ModelAdmin):
    readonly_fields = ["_image_profile", '_image_cover']
    search_fields = ['name', 'description', ]
    list_display = ('id', 'image_profile_', 'name', 'owner', 'date_creation', 'approved')
    list_filter = ('approved', 'date_creation', )

    @staticmethod
    def _image_profile(obj):
        if obj.image_profile:
            return mark_safe('<img src="{url}" width="{width}" height={height} style="max-width: 600px; max-height: 600px" />'.format(
                url=obj.image_profile.url,
                width=obj.image_profile.width,
                height=obj.image_profile.height,
                )
            )

    @staticmethod
    def _image_cover(obj):
        if obj.image_cover:
            return mark_safe('<img src="{url}" width="{width}" height={height} style="max-width: 600px; max-height: 300px" />'.format(
                url=obj.image_cover.url,
                width=obj.image_cover.width,
                height=obj.image_cover.height,
                )
            )

    @staticmethod
    def image_profile_(obj):
        if obj.image_profile:
            return mark_safe('<img src="{url}" width="60px" height="60px" />'.format(
                url=obj.image_profile.url
                )
            )


admin.site.register(CommerceCategory, CategoryAdmin)
admin.site.register(CommerceSCategoryOne, CategoryOneAdmin)
admin.site.register(CommerceSCategoryTwo, CategoryTwoAdmin)
admin.site.register(CommerceSCategory, CategorySAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(CommerceInformation, InformationAdmin)
admin.site.register(CommerceImage, ImageAdmin)
admin.site.register(CommerceRatting, RatingAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(Specification, SpecificationAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(WishList, WishListAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Compare, CompareAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLine, OrderLineAdmin)
admin.site.register(Slide, SlideAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(BillingAddress, BillingAddressAdmin)
admin.site.register(Mailing, MailingAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(MessageSupplier, MessageSupplierAdmin)
admin.site.register(Shop, ShopAdmin)
