from django.contrib import admin
from .models import Vault, Password, VaultUser


class PasswordAdmin(admin.ModelAdmin):
    pass


class VaultAdmin(admin.ModelAdmin):
    pass


# Register your models here.
admin.site.register(Password, PasswordAdmin)
admin.site.register(Vault, VaultAdmin)
admin.site.register(VaultUser)