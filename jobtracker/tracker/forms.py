from django import forms
from .models import Tracker

class TrackerEditForm(forms.ModelForm):
    class Meta:
        model = Tracker 
        fields = ['keywords', 'location', 'radius', 'salary']
