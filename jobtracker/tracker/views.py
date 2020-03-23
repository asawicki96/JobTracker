from django.shortcuts import render, redirect
from .models import Tracker 
from braces.views import LoginRequiredMixin
from .forms import TrackerEditForm, TrackerCreateForm
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from .tasks import collect_jobs, update_jobs, send_mail
# Create your views here.

class TrackerCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = TrackerCreateForm()
        context = {'form': form}
        return render(request, 'tracker/create.html', context)

    def post(self, request):
        form = TrackerCreateForm(data=request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            collect_jobs.delay(obj.id)
            send_mail.delay(obj.id)
            return redirect('dashboard')


class TrackerEditView(LoginRequiredMixin, View):
    
    def get(self, request, tracker_id):
        tracker = get_object_or_404(Tracker, id=tracker_id)
        form = TrackerEditForm(instance=tracker)
        return render(request, 'tracker/detail.html', {'form': form})
    
    def post(self, request, tracker_id):
        tracker = get_object_or_404(Tracker, id=tracker_id)
        form = TrackerEditForm(instance=tracker, data=request.POST)

        if form.is_valid():
            obj = form.save()
            collect_jobs.delay(obj.id)
        return redirect('dashboard')

    
class TrackerDeleteView(LoginRequiredMixin, View):
    def get(self, request, tracker_id):
        tracker = get_object_or_404(Tracker, id=tracker_id)
        context = { 'tracker': tracker }

        return render(request, 'tracker/delete.html', context)
    
    def post(self, request, tracker_id):
        tracker_id =request.POST.__getitem__('id')
        Tracker.objects.filter(id=tracker_id).delete()
        return redirect('dashboard')

