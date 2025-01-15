from django import forms
from ..models import Watcher, Advisor


class WatcherForm(forms.ModelForm):
    class Meta:
        model = Watcher
        fields = ['name',  'advisor', 'currency', 'type']
        widgets = {
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'advisor': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class WatcherForm2(forms.ModelForm):
    class Meta:
        model = Watcher
        fields = ["name", "active", "advisor", "currency", "type"]

    def __init__(self, *args, **kwargs):
        print("WatcherForm2", args)
        user = kwargs.pop('user', None)  # Get the user passed from the view
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['currency'].widget.attrs.update({'class': 'form-control'})
        self.fields['type'].widget.attrs.update({'class': 'form-control'})
        self.fields['advisor'].widget.attrs.update({'class': 'form-control'})
