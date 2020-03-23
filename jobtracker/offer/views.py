from django.shortcuts import render, get_object_or_404, redirect
from .models import Offer
from tracker.models import Tracker
from django.views import View
from django.views.generic.list import ListView
from braces.views import LoginRequiredMixin
from tracker.tasks import update_jobs, send_mail

# Create your views here.


class OfferListView(LoginRequiredMixin, View):
    def get(self, request, tracker_id):
        tracker = get_object_or_404(Tracker, id=tracker_id)
        offers = Offer.objects.filter(owner=tracker)

        context = {'offers': offers, 'tracker': tracker}

        return render(request, 'offer/list.html', context)

class OfferDetailView(LoginRequiredMixin, View):
    def get(self, request, offer_id):
        offer = get_object_or_404(Offer, id=offer_id)

        context = { 'offer': offer }

        return render(request, 'offer/detail.html', context)

class OfferListRefresh(LoginRequiredMixin, View):
    def get(self, request, tracker_id):
        tracker = get_object_or_404(Tracker, id=tracker_id)
        update_jobs.delay(tracker.id)
        send_mail.delay(tracker.id)
        return redirect('offer:offer_list', tracker_id)
