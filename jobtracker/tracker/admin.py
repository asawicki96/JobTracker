from django.contrib import admin
from .models import Tracker
from offer.admin import OfferInline

# Register your models here.

@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    list_diplay = ['owner', 'keywords', 'location', 'salary', 'time', 'created']
    list_filter = ['created', 'location']
    search_fields = ['owner', 'keywords']
    inlines = [OfferInline]