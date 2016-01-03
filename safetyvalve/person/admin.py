from django.contrib import admin
from .models import UserAuthentication


class UserAuthenticationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'method', 'token', 'generated')


admin.site.register(UserAuthentication, UserAuthenticationAdmin)
