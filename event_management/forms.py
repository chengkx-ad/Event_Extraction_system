from django import forms
from .models import EventType, ArgumentRole

class EventTypeForm(forms.ModelForm):
    class Meta:
        model = EventType
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ArgumentRoleForm(forms.ModelForm):
    class Meta:
        model = ArgumentRole
        fields = ['name', 'description', 'is_required']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        } 