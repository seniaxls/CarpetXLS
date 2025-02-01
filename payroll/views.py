from django.shortcuts import render
from django.http import HttpResponseForbidden
from .models import PayrollRecord
from .forms import PayrollFilterForm
import decimal
import calendar
from datetime import datetime, timedelta
from django.db.models import Count, Sum, F, Subquery, OuterRef
from orders.models import Stage  # Import the Stage model


def calculate_totals(records):
    totals = {
        'area': decimal.Decimal('0.0'),
        'additional_product_price': decimal.Decimal('0.0'),
    }

    for record in records:
        if record.area:
            totals['area'] += record.area
        if record.additional_product_price:
            totals['additional_product_price'] += record.additional_product_price


    return totals


def group_records_by_fields(records):
    grouped_records = {}

    for record in records:
        key = (
            record.status,
            record.product_name,
            record.additional_product_name,
            record.additional_product_price,

        )

        if key not in grouped_records:
            grouped_records[key] = {
                'count': 0,
                'total_area': decimal.Decimal('0.0'),
                'total_additional_product_price': decimal.Decimal('0.0'),

            }

        grouped_records[key]['count'] += 1
        if record.area:
            grouped_records[key]['total_area'] += record.area
        if record.additional_product_price:
            grouped_records[key]['total_additional_product_price'] += record.additional_product_price


    return grouped_records


def payroll_summary(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("У вас нет доступа к этой странице.")

    form = PayrollFilterForm(request.GET or None)
    grouped_records = {}
    totals = {}

    if form.is_valid():
        user = form.cleaned_data['user']
        year = int(form.cleaned_data['year']) if form.cleaned_data['year'] else None
        month = int(form.cleaned_data['month']) if form.cleaned_data['month'] else None
        status = form.cleaned_data['status']
        product_name = form.cleaned_data['product_name']
        additional_product_name = form.cleaned_data['additional_product_name']

        start_date = None
        end_date = None

        if year and month:
            last_day_of_month = calendar.monthrange(year, month)[1]
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month, last_day_of_month, 23, 59, 59)

        query = PayrollRecord.objects.all()

        if user:
            query = query.filter(user=user)
        if start_date and end_date:
            query = query.filter(order__create_date_time__range=(start_date, end_date))
        if status:
            query = query.filter(status=status.name)
        if product_name:
            query = query.filter(product_name=product_name.product_name)
        if additional_product_name:
            query = query.filter(additional_product_name=additional_product_name.product_name)

        # Sorting by stage group_stage, then by product_name and additional_product_name
        stage_order_subquery = Stage.objects.filter(name=OuterRef('status')).values('group_stage')[:1]
        records = query.annotate(
            stage_order=Subquery(stage_order_subquery)
        ).order_by('stage_order', 'product_name', 'additional_product_name')

        grouped_records = group_records_by_fields(records)
        totals = calculate_totals(records)

    context = {
        'form': form,
        'grouped_records': grouped_records,
        'totals': totals
    }

    return render(request, 'payroll/payroll_summary.html', context)