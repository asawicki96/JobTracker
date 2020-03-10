from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
# Create your views here.

class IndexView(TemplateView):
    template_name = 'base.html'

class AccountRegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = form.save()
        login(self.request, user)
        return result

