from django import forms
from .models import Annotation, EventAnnotation, ArgumentAnnotation

class AnnotationForm(forms.ModelForm):
    class Meta:
        model = Annotation
        fields = ['status', 'review_comment']
        widgets = {
            'review_comment': forms.Textarea(attrs={'rows': 3}),
        }

class EventAnnotationForm(forms.ModelForm):
    class Meta:
        model = EventAnnotation
        fields = ['event_type', 'text', 'start_offset', 'end_offset']
        widgets = {
            'start_offset': forms.HiddenInput(),
            'end_offset': forms.HiddenInput(),
        }

    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event_type'].queryset = project.event_types.all()

class ArgumentAnnotationForm(forms.ModelForm):
    class Meta:
        model = ArgumentAnnotation
        fields = ['role', 'text', 'start_offset', 'end_offset']
        widgets = {
            'start_offset': forms.HiddenInput(),
            'end_offset': forms.HiddenInput(),
        }

    def __init__(self, event_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].queryset = event_type.argument_roles.all()

class AnnotationReviewForm(forms.ModelForm):
    class Meta:
        model = Annotation
        fields = ['status', 'review_comment']
        widgets = {
            'review_comment': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [
            ('reviewed', '通过'),
            ('rejected', '驳回'),
        ] 