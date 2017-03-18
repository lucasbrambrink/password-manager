from django.contrib import admin
from .models import Vault, DomainName, VaultUser


class PasswordAdmin(admin.ModelAdmin):
    pass


class VaultAdmin(admin.ModelAdmin):
    pass


# Register your models here.
admin.site.register(DomainName, PasswordAdmin)
admin.site.register(Vault, VaultAdmin)
admin.site.register(VaultUser)