from django.contrib import admin
from .models import Offer
# Register your models here.


class OfferInline(admin.StackedInline):
    model = Offer
    extra = 1

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'salary', 'updated', 'order', 'owner']
    search_fields = ['title', 'location', 'owner']
