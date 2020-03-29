from django.shortcuts import render, redirect
from .models import Tracker 
from braces.views import LoginRequiredMixin
from .forms import TrackerForm
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from .tasks import collect_jobs, update_jobs, send_mail
from offer.models import Offer

# Create your views here.


class TrackerCreateView(LoginRequiredMixin, View):
    
    """ Displays Tracker create form """

    def get(self, request):
        form = TrackerForm()
        context = {'form': form}
        return render(request, 'tracker/create.html', context)

    """ Validates incoming form and collect offers.
        Redirects to dashboard. """

    def post(self, request):
        form = TrackerForm(data=request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            collect_jobs.delay(obj.id)
            return redirect('dashboard')
        return render(request, 'tracker/detail.html', {'form': form})


class TrackerEditView(LoginRequiredMixin, View):
    
    """ Displays Tracker edit form """

    def get(self, request, tracker_id):
        tracker = get_object_or_404(Tracker, id=tracker_id)
        form = TrackerForm(instance=tracker)
        return render(request, 'tracker/detail.html', {'form': form})
    
    """ Validates incoming form and save changes in Tracker object.
        Deletes offers belonging. 
        Collect new offers.
        Redirects to dashboard. """

    def post(self, request, tracker_id):
        args = {}
        tracker = get_object_or_404(Tracker, id=tracker_id)
        form = TrackerForm(instance=tracker, data=request.POST)

        if form.is_valid():
            obj = form.save()
            eldest_offers = Offer.objects.filter(owner=obj)
            if eldest_offers:
                eldest_offers.delete()
                
            collect_jobs.delay(obj.id)
            return redirect('dashboard')
        return render(request, 'tracker/detail.html', {'form': form})

    
class TrackerDeleteView(LoginRequiredMixin, View):

    """ Displays delete confirmation button """

    def get(self, request, tracker_id):
        tracker = get_object_or_404(Tracker, id=tracker_id)
        context = { 'tracker': tracker }

        return render(request, 'tracker/delete.html', context)
    
    """ Deletes tracker and redirects do dashboard """

    def post(self, request, tracker_id):
        tracker_id =request.POST.__getitem__('id')
        Tracker.objects.filter(id=tracker_id).delete()
        return redirect('dashboard')

