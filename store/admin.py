from django import forms
from django.contrib import admin
from django.forms import ModelForm
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilter

from .models import Customer, Product, Order, OrderItem, ShippingAddress, ProductImage, Category, Carousel


# Change 'PRODUCT' to 'Товар' in Category TabularInline form
class CategoryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].label = 'Товар'


# https://docs.djangoproject.com/en/4.0/ref/contrib/admin/#working-with-many-to-many-models
class CategoryInline(admin.TabularInline):
    model = Product.category.through
    # form = CategoryForm
    verbose_name = "Товар"
    verbose_name_plural = "Товары"
    extra = 0

    # Add filter_horizontal/filter_vertical to Category TabularInline
    # Source: https://stackoverflow.com/questions/65662152/how-to-use-filter-horizontal-with-tabularinline-and-through
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "product":
    #         kwargs['queryset'] = Product.objects.all()
    #
    #         # this line causes error "Select a valid choice. That choice is not one of the available choices."
    #     kwargs["widget"] = widgets.FilteredSelectMultiple(verbose_name="Товары", is_stacked=False)
    #     # kwargs["widget"] = CheckboxSelectMultiple()
    #         # kwargs['widget'] = widgets.FilteredSelectMultiple(db_field.verbose_name,db_field.name in self.filter_vertical)
    #         # kwargs["widget"] = widgets.FilteredSelectMultiple(db_field.remote_field, self.admin_site)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)
    #
    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     vertical = False
    #     kwargs["widget"] = widgets.FilteredSelectMultiple(db_field.verbose_name,vertical,)
    #     # kwargs["widget"] = widgets.AutocompleteSelectMultiple(db_field, admin_site=self.admin_site)
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)


class CategoryAdmin(admin.ModelAdmin):

    @admin.action(description="Изображение категории")
    def image_tag(self, obj):
        """Display actual image on the Category page"""
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width=300 />')

    def get_readonly_fields(self, request, obj=None):
        """Show category image only if it exists"""
        if obj and not obj.image:
            return []
        else:
            return self.readonly_fields


    readonly_fields = ('image_tag',)

    inlines = [CategoryInline]
    exclude = ('category',)

    list_display = ('name', 'short_description', 'is_popular')
    list_editable = ('is_popular',)

    # hide Product_category object (2)
    class Media:
        css = {"all": ("css/hide_admin_original.css",),}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'active', 'is_popular', 'show_categories')
    list_editable = ('active', 'is_popular')
    inlines = [ProductImageInline]
    filter_horizontal = ('category',)

    @admin.action(description="Категории")
    def show_categories(self, obj):
        return " | ".join([category.name for category in obj.category.all()])


class OrderInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    def has_change_permission(self, request, obj=None):
        return True

class ShippingAddressInline(admin.TabularInline):
    model = ShippingAddress
    fields = ('phone_number', 'address', 'city', 'zipcode')
    readonly_fields = ('phone_number', 'address', 'city', 'zipcode')

    # ability to change address from Order Detail view
    show_change_link = True
    extra = 0

class OrderAdmin(admin.ModelAdmin):

    # @admin.action
    def get_complete_orders(self, obj):
        if Order.complete == True:
            return obj.fields["complete"]
        else:
            return "N/A"

    # is_staff can only see complete orders, is_superuser sees everything
    def get_queryset(self, request):
        queryset = super(OrderAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(complete=True)

    list_display = ('date_ordered', 'customer', 'get_customer_email', 'get_order_items',
                    'get_cart_total',
                'status', 'is_paid', 'complete')

    # complete = "Send Order" button was clicked
    # only superuser can see "complete" field
    def changelist_view(self, request, extra_context=None):
        if not request.user.is_superuser:
            self.list_display = ('date_ordered', 'customer', 'get_customer_email',
                                 'get_order_items', 'get_cart_total',
                        'status', 'is_paid')
        else:
            self.list_display = ('date_ordered', 'customer', 'get_customer_email',
                                 'get_order_items', 'get_cart_total',
                                 'status', 'is_paid', 'complete')
        return super(OrderAdmin, self).changelist_view(request, extra_context)

    # Don't allow non-superuser to save in Edit page or Order
    # source: https://stackoverflow.com/a/43680118/15015225
    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     if not request.user.is_superuser:
    #         extra_context = extra_context or {}
    #         extra_context['show_save_and_continue'] = False
    #         extra_context['show_save'] = False
    #         extra_context['show_save_and_add_another'] = False
    #     return super(OrderAdmin, self).change_view(request, object_id, extra_context=extra_context)

    # non-superuser cannot edit certain fields
    # source: https://stackoverflow.com/a/4346448/15015225
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(OrderAdmin, self).get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            if obj:  # editing an existing object
                return readonly_fields + ('customer', 'complete')
        return readonly_fields

# https://github.com/silentsokolov/django-admin-rangefilter
    list_filter = (('date_ordered', DateRangeFilter), 'date_ordered', 'status', 'is_paid')
    list_editable = ('status', 'is_paid')
    search_fields = ('customer__user__name', 'customer__user__email')
    inlines = [OrderInline, ShippingAddressInline]
    search_help_text = "Имя или e-mail покупателя"




class CarouselForm(ModelForm):
    def clean(self):
        cleaned_data = super(CarouselForm, self).clean()
        category = cleaned_data.get('category', None)
        product = cleaned_data.get('product', None)
        if category and product:
             raise forms.ValidationError("Выберите либо категорию, либо товар.")

    class Meta:
        model = Carousel
        fields = ['category', 'product', 'banner', 'title', 'description', 'is_enabled']

class CarouselAdmin(admin.ModelAdmin):
    form = CarouselForm
    list_display = ('get_product_or_category', 'title', 'description', 'is_enabled')
    list_editable = ('title', 'description', 'is_enabled')

    # Visually more pleasing than having "category" and "product" as separate fields since one is always empty if
    # the other is not
    def get_product_or_category(self, obj):
        return obj

    get_product_or_category.short_description = "Товар/Категория"


class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('address', 'customer', 'date_added')


admin.site.register(Customer)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(Carousel, CarouselAdmin)
