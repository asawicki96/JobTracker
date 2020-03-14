from django.shortcuts import render, redirect
from .models import Tracker 
from braces.views import LoginRequiredMixin
from .forms import TrackerEditForm
from django.shortcuts import get_object_or_404
from django.views import View

# Create your views here.

class TrackerEditView(LoginRequiredMixin, View):
    
    def get(self, request, tracker_id):
        tracker = get_object_or_404(Tracker, id=tracker_id)
        form = TrackerEditForm(instance=tracker)
        return render(request, 'tracker/detail.html', {'form': form})
    
    def post(self, request, tracker_id):
        tracker = get_object_or_404(Tracker, id=tracker_id)
        form = TrackerEditForm(instance=tracker, data=request.POST)

        if form.is_valid():
            form.save()
        return redirect('dashboard')

    
