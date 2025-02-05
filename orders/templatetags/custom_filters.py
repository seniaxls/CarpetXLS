from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def replace_user_id_with_name(value):
    try:
        if "user" in value:
            parts = value.split("(")
            user_id = parts[1].split(")")[0]
            username = User.objects.get(id=user_id).username
            return value.replace(f"({user_id})", f"({username})")
        return value
    except Exception:
        return value