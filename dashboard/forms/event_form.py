from django import forms
from ..models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['type', 'description']  # Fields to include in the form
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }


class EventForm2(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['description', 'parent', 'type', 'value', 'date']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
