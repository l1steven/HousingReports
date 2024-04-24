from django import forms
from loginApp.models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['name', 'location', 'description', 'upload']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'upload': forms.fileInput(attrs={'class': 'form-control', 'multiple': True}),
        }

class AnonymousComplaintForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AnonymousComplaintForm, self).__init__(*args, **kwargs)
        self.fields['name'].initial = 'Anonymous'
        self.fields['name'].widget.attrs['readonly'] = True
        self.fields['is_anonymous'].initial = True
        self.fields['is_anonymous'].widget = forms.HiddenInput()

    class Meta:
        model = Complaint
        fields = ['name', 'location', 'description', 'upload', 'is_anonymous']
        widgets = {
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'upload': forms.ClearableFileInput(attrs={'class': 'form-control', 'multiple': True}),
        }
