from extra_settings.models import Setting
from django.utils.timezone import localtime
from simple_history.admin import SimpleHistoryAdmin
from django.shortcuts import render, redirect
import decimal
from django.utils.html import format_html
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import *
from django.urls import reverse


class ProductOrderInline(admin.TabularInline):
    model = ProductOrder
    template = "admin/orders/Order/myinline.html"
    classes = ['collapse']
    fields = ['message', 'width', 'height', 'product_add', 'overlock', 'allowance', 'comment']
    readonly_fields = ['message']

    def has_add_permission(self, request, obj=None):
        if obj and hasattr(obj, 'stage') and obj.stage.group_stage >= 2:
            return False
        return super().has_add_permission(request, obj)

    def get_fields(self, request, obj=None):
        fields = ['product', 'width', 'height', 'product_add', 'overlock', 'allowance', 'comment']
        if obj and obj.stage and obj.stage.group_stage >= 2:
            fields = ('message', 'overlock', 'allowance', 'comment')
        return fields

    def get_extra(self, request, obj=None, **kwargs):
        extra = 1
        if obj and ProductOrder.objects.filter(order_id=obj.id).exists():
            extra = 0
        return extra


class SecondProductOrderInline(admin.TabularInline):
    model = SecondProductOrder
    classes = ['collapse']
    template = "admin/orders/Order/myinline.html"

    def get_fields(self, request, obj=None):
        return ["product", "second_amount"]

    def get_extra(self, request, obj=None, **kwargs):
        extra = 1
        if obj and SecondProductOrder.objects.filter(order_id=obj.id).exists():
            extra = 0
        return extra


@admin.register(GroupStagePermission)
class GroupStagePermissionAdmin(admin.ModelAdmin):
    list_display = ('group', 'get_stages', 'days_limit')
    filter_horizontal = ('stages',)

    def get_stages(self, obj):
        return ', '.join([stage.name for stage in obj.stages.all()])

    get_stages.short_description = "Доступные этапы"


class DateFilterBase(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return (
            ('today', _('Сегодня')),
            ('yesterday', _('Вчера')),
            ('last_3_days', _('Последние 3 дня')),
            ('last_week', _('Последняя неделя')),
        )

    def _get_date_range(self, value):
        now = timezone.now()
        if value == 'today':
            return (now.date(), now.date())
        elif value == 'yesterday':
            yesterday = now - timezone.timedelta(days=1)
            return (yesterday.date(), yesterday.date())
        elif value == 'last_3_days':
            start_date = now - timezone.timedelta(days=3)
            return (start_date.date(), now.date())
        elif value == 'last_week':
            start_date = now - timezone.timedelta(days=7)
            return (start_date.date(), now.date())
        return None


class CreateDateFilter(DateFilterBase):
    title = _('Дата создания')
    parameter_name = 'create_date'

    def queryset(self, request, queryset):
        date_range = self._get_date_range(self.value())
        if date_range:
            start_date, end_date = date_range
            return queryset.filter(create_date__range=(start_date, end_date))
        return queryset


class UpdateDateFilter(DateFilterBase):
    title = _('Дата редактирования')
    parameter_name = 'updated_at'

    def queryset(self, request, queryset):
        date_range = self._get_date_range(self.value())
        if date_range:
            start_date, end_date = date_range
            return queryset.filter(updated_at__date__range=(start_date, end_date))
        return queryset


class StageFilter(admin.SimpleListFilter):
    title = _('Этап')
    parameter_name = 'stage'

    def lookups(self, request, model_admin):
        accessible_stage_ids = GroupStagePermission.get_accessible_stages(request.user)
        accessible_stages = Stage.objects.filter(id__in=accessible_stage_ids)
        return [(stage.id, stage.name) for stage in accessible_stages]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(stage_id=self.value())
        return queryset


class CheckCallFilter(admin.SimpleListFilter):
    title = 'Нужно позвонить'
    parameter_name = 'check_call'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(check_call=True)
        if self.value() == 'no':
            return queryset.filter(check_call=False)


class OrderAdmin(SimpleHistoryAdmin):
    history_list_display = ['changed_fields']
    list_per_page = 15
    inlines = [ProductOrderInline, SecondProductOrderInline]
    autocomplete_fields = ['client']
    search_fields = ['client__fio', 'id', 'order_sum', 'order_number', 'client__address', 'client__phone_number']
    list_display = (
        'order_number', 'client', 'client_phone_number', 'check_call', 'order_sum', 'stage', 'formatted_created_at',
        'formatted_updated_at', 'formatted_target_date'
    )
    list_display_links = (
        'order_number', 'client', 'client_phone_number', 'order_sum', 'stage'
    )
    list_filter = (CreateDateFilter, UpdateDateFilter, CheckCallFilter, StageFilter)
    list_editable = ['check_call']
    change_form_template = "admin/orders/Order/change_form.html"

    def formatted_created_at(self, obj):
        if obj.created_at:
            local_time = localtime(obj.created_at)
            return local_time.strftime('%d.%m (%H:%M)')
        return '-'

    formatted_created_at.short_description = 'Дата создания'

    def formatted_updated_at(self, obj):
        if obj.updated_at:
            local_time = localtime(obj.updated_at)
            return local_time.strftime('%d.%m (%H:%M)')
        return '-'

    formatted_updated_at.short_description = 'Дата обновления'

    def formatted_target_date(self, obj):
        if obj.target_date:
            return obj.target_date.strftime('%d.%m')
        return '-'

    formatted_target_date.short_description = 'Целевая дата'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        readonly_fields = ('order_sum', 'message_for_order', 'first_message', 'second_message',
                           'client_address', 'client_phone_number')
        if obj and obj.stage and obj.stage.group_stage >= 2:
            readonly_fields += ('client',)
        return readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        accessible_stage_ids = GroupStagePermission.get_accessible_stages(request.user)
        qs = qs.filter(stage_id__in=accessible_stage_ids)
        days_limit = GroupStagePermission.get_days_limit(request.user)
        if days_limit is not None:
            cutoff_date = timezone.now() - timezone.timedelta(days=days_limit)
            qs = qs.filter(updated_at__gte=cutoff_date)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['stage'].queryset = Order.get_available_stages(request.user, obj=obj)
        form.base_fields['stage'].empty_label = None
        return form

    def save_model(self, request, obj, form, change):
        obj.history_user = request.user
        if 'check_call' in form.changed_data:
            obj._manual_check_call_change = True
        super().save_model(request, obj, form, change)

    class Media:
        js = ["admin_custom.js"]

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (
                None,
                {
                    "fields": [
                        ('client', 'stage', 'check_call', "target_date"),
                        ("comment",),
                        ('order_sum', 'client_address', 'client_phone_number'),
                    ],
                },
            ),
            (
                "Оплата",
                {
                    "classes": ["collapse"],
                    "fields": ['user'],
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
            order.stage = Stage.objects.get(name='Чистый-Склад')
            order.save()

    actions = [make_beating, make_washing, make_finishing, make_clean_warehouse]


class ProductUnitEdite(admin.ModelAdmin):
    readonly_fields = ['size_numb', 'size_name', 'size_name_short']


admin.site.register(Order, OrderAdmin)
admin.site.register(Product)
admin.site.register(ProductAdd)
admin.site.register(SecondProduct)
admin.site.register(Stage)
admin.site.register(ProductUnit, ProductUnitEdite)

admin.site.site_header = 'carpetxls'
admin.site.site_title = ''
admin.site.index_title = ''