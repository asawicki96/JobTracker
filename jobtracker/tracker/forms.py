from django import forms
from .models import Tracker


class TrackerForm(forms.ModelForm):
    class Meta:
        model = Tracker 
        fields = ['keywords', 'location', 'radius', 'salary']

    def clean(self):
        cleaned_data = super().clean()
        location = cleaned_data.get('location')
        radius = cleaned_data.get('radius')
        salary = cleaned_data.get('salary')

        if location == None and radius != None:
            self.add_error('radius', 'Radius cannot be set when there is no location')
        if salary:
            if salary < 3500 or salary > 20000:
                raise forms.ValidationError({'salary': 'Salary must be greater or equal to 3500 and lesser or equal to 20000'})