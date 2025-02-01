from django.contrib import admin
from django.template.defaultfilters import first
from extra_settings.models import Setting
from django import forms
from itertools import chain
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.defaulttags import url
from django.urls import resolve
from django.utils.translation import gettext
from pyexpat.errors import messages
from django.urls import path
from django.db.models import Q
from datetime import date
from django.contrib import admin
from .models import Order, ProductOrder, Stage
from payroll.models import PayrollRecord
import decimal

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import *


# Register your models here.
# Register your models here.


class SecondProductOrderForm(forms.ModelForm):
    class Meta:
        model = SecondProductOrder
        fields = ()


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ()
        exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.check_stage_hide:
            if self.instance.check_stage_hide == 1:
                self.fields["stage"].queryset = Stage.objects.filter(group_stage=1).all().order_by('id')
            if self.instance.check_stage_hide == 2:
                self.fields["stage"].queryset = Stage.objects.filter(
                    Q(group_stage=1, super_stage=True) | Q(group_stage=2)).all().order_by('id')
            if self.instance.check_stage_hide == 3:
                self.fields["stage"].queryset = Stage.objects.filter(
                    Q(group_stage=2, super_stage=True) | Q(group_stage=3)).all().order_by('id')
            if self.instance.check_stage_hide == 4:
                self.fields["stage"].queryset = Stage.objects.filter(
                    Q(group_stage=3, super_stage=True) | Q(group_stage=4)).all().order_by('id')
            if self.instance.check_stage_hide == 5:
                self.fields["stage"].queryset = Stage.objects.filter(
                    Q(group_stage=4, super_stage=True) | Q(group_stage=5)).all().order_by('id')
            if self.instance.check_stage_hide == 6:
                self.fields["stage"].queryset = Stage.objects.filter(
                    Q(group_stage=5, super_stage=True) | Q(group_stage=6)).all().order_by('id')

            if self.instance.check_stage_hide == 7:
                self.fields["stage"].queryset = Stage.objects.filter(
                    Q(group_stage=6, super_stage=True) | Q(group_stage=7)).all().order_by('id')

            if self.instance.check_stage_hide == 8:
                if self.instance.user.is_superuser:
                    self.fields["stage"].queryset = Stage.objects.filter(
                        Q(group_stage=7, super_stage=True) | Q(group_stage=8)).all().order_by('id')
                else:
                    self.fields["stage"].queryset = Stage.objects.filter(
                        Q(group_stage=7, super_stage=True) | Q(group_stage=8, super_stage=False)).all().order_by('id')


class ProductOrderForm(forms.ModelForm):
    class Meta:
        model = ProductOrder
        fields = ()


# Проверка введеных значений чтоб не было отрицательных


class MembershipInline(admin.TabularInline):
    model = ProductOrder
    form = ProductOrderForm
    template = "admin/orders/Order/myinline.html"
    classes = ['collapse']

    def get_extra(self, request, obj=None, **kwargs):
        extra = 1
        if obj:
            if ProductOrder.objects.filter(order_id=obj.id).exists():
                extra = 0
        return extra

    def get_fields(self, request, obj=None):
        if obj:
            if 8 > obj.check_stage_hide >= 4:
                return ['message', "overlock", "allowance", 'comment']
            elif obj.check_stage_hide >= 8:
                return ['message', 'comment']
            else:
                return ['message', "product", ("height", "width"), "product_add", "overlock", "allowance", 'comment']
        else:
            return ['message', "product", ("height", "width"), "product_add", "overlock", "allowance", 'comment']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if 8 >= obj.check_stage_hide >= 7:
                return ["message", 'comment']
            return ["message", ]
        else:
            return ["message", ]


class MembershipInline2(admin.TabularInline):
    form = SecondProductOrderForm
    model = SecondProductOrder
    classes = ['collapse']
    template = "admin/orders/Order/myinline.html"

    def get_fields(self, request, obj=None):
        return ["product", "second_amount", ]

    def get_extra(self, request, obj=None, **kwargs):
        extra = 1
        if obj:
            if SecondProductOrder.objects.filter(order_id=obj.id).exists():
                extra = 0
        return extra


# class SecondProductListFilter(admin.SimpleListFilter):
#
#     title = "Допы"
#
#     parameter_name = "second_stage"
#
#     def lookups(self, request, model_admin):
#
#       return [
#         ("1", 'Запах'),
#         ("2", 'Грязь'),
#         ("3", 'Вычесать'),
#         ("4", 'Парфюм'),
#         ("5", 'Оверлок'),
#       ]
#
#     def queryset(self, request, queryset):
#
#       if self.value() == "1":
#         return queryset.filter(product_order__add_service_prod1=True)
#       if self.value() == "2":
#         return queryset.filter(product_order__add_service_prod2=True)
#       if self.value() == "3":
#         return queryset.filter(product_order__add_service_prod3=True)
#       if self.value() == "4":
#         return queryset.filter(product_order__add_service_prod4=True)
#       if self.value() == "5":
#         return queryset.filter(product_order__add_service_prod5=True)


class OrderEdite(admin.ModelAdmin):
    form = OrderForm
    inlines = [MembershipInline, MembershipInline2]
    autocomplete_fields = ['client', ]
    search_fields = ['client__fio', 'id', 'order_sum', 'order_number', 'client__address', 'client__phone_number']
    list_display = (
    'order_number', 'client', 'client_phone_number', 'check_call', 'order_sum', 'stage', 'create_date', 'target_date')
    list_display_links = (
    'order_number', 'client', 'client_phone_number', 'order_sum', 'create_date', 'target_date', 'stage')
    list_filter = ['stage', 'create_date', ]
    # list_filter = ('stage', 'create_date','secondproductorder__stage','product_order__add_service_prod1','product_order__add_service_prod3','product_order__add_service_prod4','product_order__add_service_prod5')
    list_editable = ['check_call']
    change_form_template = "admin/orders/Order/change_form.html"

    class Media:
        js = ["admin_custom.js"]

    def get_fieldsets(self, request, obj=None):

        fieldsets = [
            (
                None,

                {

                    # "fields": [('client', 'stage', 'check_call'), ( 'order_sum','client_address'),'check_stage_hide'],
                    "fields": [('client', 'stage', 'check_call'),
                               ('order_sum', 'client_address', 'client_phone_number'), ],
                },
            ),

            (
                "Дополнительно",
                {
                    "classes": ["collapse"],
                    "fields": ['create_date_time', "target_date", "comment", 'user'],
                },
            ),
        ]

        if Setting.get('MESSAGE_FOR_ORDER_EDU_ACTIVE'):
            fieldsets[0][1]['fields'].append(('first_message', 'second_message'))

        if Setting.get('MESSAGE_FOR_ORDER_ACTIVE'):
            fieldsets[0][1]['fields'].append(('message_for_order'))

        return fieldsets

    def client_address(self, obj):
        if obj.client:
            return obj.client.address

    def client_phone_number(self, obj):
        if obj.client:
            return obj.client.phone_number

    client_phone_number.short_description = 'Телефон'

    def message_for_order(self, order: Order):
        value = Setting.get("MESSAGE_FOR_ORDER", default="django-extra-settings")

        return value

    def first_message(self, order: Order):

        value = Setting.get("MESSAGE_FOR_ORDER_FIRST", default="django-extra-settings")

        if order.pk:
            value = Order.objects.get(pk=order.pk).stage.first_message
            if value is None:
                value = ''

        return value

    def second_message(self, order: Order):
        value = Setting.get("MESSAGE_FOR_ORDER_SECOND", default="django-extra-settings")

        if order.pk:
            value = Order.objects.get(pk=order.pk).stage.second_message
            if value is None:
                value = ''

        return value

    client_address.short_description = 'Адрес'
    message_for_order.short_description = 'Внимание'
    first_message.short_description = 'Внимание2'
    second_message.short_description = 'Внимание3'

    def get_readonly_fields(self, request, obj=None):

        return ['order_sum', 'create_date_time', 'message_for_order', 'first_message', 'second_message',
                'client_address', 'client_phone_number']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(id=request.user.id)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_sortable_by(self, request):
        return {*self.get_list_display(request)} - {"order_sum"} - {'check_call'} - {"client"}

    def calculate_product_area(self, product_order):
        width = product_order.width or decimal.Decimal('0.0')
        height = product_order.height or decimal.Decimal('0.0')
        return width * height

    def calculate_additional_product_area(self, additional_product, area):
        if additional_product.product_unit.size_numb == 32:
            return area
        return None

    def create_payroll_records(self, orders, new_status, user):
        valid_stages = ['Грязный-Склад', 'Выбивание', 'Стирка', 'Финишка']
        stage_order = {stage.name: index for index, stage in
                       enumerate(Stage.objects.filter(name__in=valid_stages).order_by('group_stage'))}

        for order in orders:
            print(orders)
            current_stage_name = order.stage.name if order.stage else None
            if current_stage_name not in stage_order:
                self.message_user(request,
                                  f"Заказ {order.order_number} не может быть обработан: Начальный статус должен быть один из {valid_stages}.",
                                  level='error')
                continue

            target_stage_index = stage_order[new_status]
            current_stage_index = stage_order[current_stage_name]

            if current_stage_index > target_stage_index:
                self.message_user(request,
                                  f"Заказ {order.order_number} не может быть обработан: Нельзя перейти на более ранний статус.",
                                  level='error')
                continue

            stages_to_process = [stage for stage in valid_stages if
                                 stage_order[stage] > current_stage_index and stage_order[stage] <= target_stage_index]
            for stage_name in stages_to_process:

                if stage_name == 'Выбивание':
                    order.stage = Stage.objects.get(name=stage_name)
                    order.save()
                elif stage_name == 'Стирка':
                    order.stage = Stage.objects.get(name=stage_name)
                    order.save()

                elif stage_name == 'Финишка':
                    order.stage = Stage.objects.get(name=stage_name)
                    order.save()




    @admin.action(description='Перейти на статус Выбивание')
    def make_beating(self, request, queryset):
        valid_initial_stages = ['Грязный-Склад']
        for order in queryset:
            if order.stage.name not in valid_initial_stages:
                self.message_user(request,
                                  f"Заказ {order.order_number} не может быть обработан: Начальный статус должен быть один из {valid_initial_stages}.",
                                  level='error')
                return
        self.create_payroll_records(queryset, 'Выбивание', request.user)

    @admin.action(description='Перейти на статус Стирка')
    def make_washing(self, request, queryset):
        valid_initial_stages = ['Грязный-Склад', 'Выбивание']
        for order in queryset:
            if order.stage.name not in valid_initial_stages:
                self.message_user(request,
                                  f"Заказ {order.order_number} не может быть обработан: Начальный статус должен быть один из {valid_initial_stages}.",
                                  level='error')
                return
        self.create_payroll_records(queryset, 'Стирка', request.user)

    @admin.action(description='Перейти на статус Финишка')
    def make_finishing(self, request, queryset):
        valid_initial_stages = ['Грязный-Склад', 'Выбивание', 'Стирка']
        for order in queryset:
            if order.stage.name not in valid_initial_stages:
                self.message_user(request,
                                  f"Заказ {order.order_number} не может быть обработан: Начальный статус должен быть один из {valid_initial_stages}.",
                                  level='error')
                return
        self.create_payroll_records(queryset, 'Финишка', request.user)

    @admin.action(description='Перейти на статус Чистый-Склад')
    def make_clean_warehouse(self, request, queryset):
        valid_initial_stages = ['Финишка']
        for order in queryset:
            if order.stage.name not in valid_initial_stages:
                self.message_user(request,
                                  f"Заказ {order.order_number} не может быть обработан: Начальный статус должен быть один из {valid_initial_stages}.",
                                  level='error')
                return
        for order in queryset:
            order.stage = Stage.objects.get(name='Чистый-Склад')
            order.save()
            # Не создаем записи в PayrollRecord для этого статуса

    actions = [ make_beating, make_washing, make_finishing, make_clean_warehouse]

class ProductUnitEdite(admin.ModelAdmin):
    readonly_fields = ['size_numb', 'size_name', 'size_name_short']


admin.site.register(ProductOrder)
admin.site.register(Order, OrderEdite)

admin.site.register(Product)
admin.site.register(ProductAdd)
admin.site.register(SecondProduct)
admin.site.register(SecondProductOrder)
admin.site.register(Stage)
admin.site.register(ProductUnit, ProductUnitEdite)

admin.site.site_header = 'carpetxls'
admin.site.site_title = ''
admin.site.index_title = ''

# class ChangeLogAdmin(admin.ModelAdmin):
#   list_display = ('order', 'stage', 'creator', 'created_date',)
#   readonly_fields = ('order', 'stage', 'creator', 'created_date',)
#   list_filter = ('order', 'stage',)
