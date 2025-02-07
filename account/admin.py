from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# Создаем собственную форму для User
class CustomUserChangeForm(forms.ModelForm):
    patronymic = forms.CharField(
        max_length=100,
        required=False,
        label="Отчество",
        widget=forms.TextInput(attrs={'class': 'vTextField'})  # Добавляем класс vTextField
    )

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализируем значение отчества из связанного профиля
        if self.instance and hasattr(self.instance, 'userprofile'):
            self.fields['patronymic'].initial = self.instance.userprofile.patronymic

    def save(self, commit=True):
        user = super().save(commit=False)
        # Сохраняем отчество в связанном профиле
        patronymic = self.cleaned_data.get('patronymic')
        if hasattr(user, 'userprofile'):
            user.userprofile.patronymic = patronymic
            if commit:
                user.userprofile.save()
        return user

# Расширяем админку User
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm  # Используем нашу кастомную форму

    # Добавляем отчество в список отображаемых полей
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_patronymic')

    # Добавляем отчество в форму редактирования
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {
            'fields': ('last_name','first_name', 'patronymic')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    # Метод для получения отчества из связанного профиля
    def get_patronymic(self, obj):
        return obj.userprofile.patronymic
    get_patronymic.short_description = 'Отчество'

# Перерегистрируем User с новой админкой
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)