from django.shortcuts import render
from django.views.generic import TemplateView


class VaultView(TemplateView):
    template_name = u'vault/vault.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            u'passwords': []
        })
