from django.contrib import admin
from .models import *

class PhoneEditor(admin.ModelAdmin):

  list_display = ['phone_number','fio','city','street','home','apartment','entrance']
  list_display_links = ['fio','phone_number','fio','city','street','home','apartment','entrance']
  search_fields = ['phone_number','address','fio']
  change_form_template = "admin/clients/Client/change_form.html"

  def get_fields(self, request, obj=None):
    if request.user.is_superuser:
      return ('phone_number','fio','comment','city','street','home','apartment','entrance','organization','address')
    else:
      return ('phone_number','fio','comment','city','street','home','apartment','entrance')


admin.site.register(Client,PhoneEditor)


 