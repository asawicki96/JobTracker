from django.shortcuts import render, get_object_or_404, redirect
from .models import Offer
from tracker.models import Tracker
from django.views import View
from django.views.generic.list import ListView
from braces.views import LoginRequiredMixin
from tracker.tasks import update_jobs
import requests

# Create your views here.

""" Displays list of Offer objects belonging to one Tracker instance """

class OfferListView(LoginRequiredMixin, View):
    def get(self, request, tracker_id):
        tracker = get_object_or_404(Tracker, id=tracker_id)
        offers = Offer.objects.filter(owner=tracker)

        context = {'offers': offers, 'tracker': tracker}

        return render(request, 'offer/list.html', context)

""" Updates offers belonging to one Tracker instance and refreshes current site """

class OfferListRefresh(LoginRequiredMixin, View):
    def get(self, request, tracker_id):
        tracker = get_object_or_404(Tracker, id=tracker_id)
        update_jobs.delay(tracker.id)
        return redirect('offer:offer_list', tracker_id)

