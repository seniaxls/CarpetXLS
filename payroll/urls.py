from django.urls import path
from . import views

urlpatterns = [
    path('payroll-summary/', views.payroll_summary, name='payroll-summary'),
]