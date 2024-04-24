from django import forms
from loginApp.models import Complaint
from django.forms import ClearableFileInput

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

class ComplaintForm(forms.ModelForm):

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
    class Meta:
        model = Complaint
        fields = ['name', 'location', 'description', 'upload']
        upload = MultipleFileField(label='Select files', required=False)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

class AnonymousComplaintForm(forms.ModelForm):

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].initial = 'Anonymous'
        self.fields['name'].widget.attrs['readonly'] = True
        self.fields['is_anonymous'].initial = True
        self.fields['is_anonymous'].widget = forms.HiddenInput()

    class Meta:
        model = Complaint
        fields = ['name', 'location', 'description', 'upload', 'is_anonymous']
        upload = MultipleFileField(label='Select files', required=False)

        widgets = {
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
