from django import forms
from .models import Document, DocumentBatch

class DocumentForm(forms.ModelForm):
    file = forms.FileField(
        label='文件',
        help_text='支持txt、doc、docx、pdf格式',
        widget=forms.FileInput(attrs={'class': 'form-control-file'})
    )
    
    class Meta:
        model = Document
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DocumentBatchForm(forms.ModelForm):
    class Meta:
        model = DocumentBatch
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class DocumentAssignForm(forms.Form):
    annotator = forms.ModelChoiceField(
        queryset=None,
        label='分配给',
        empty_label='请选择标注者',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 只显示项目中的标注者
        self.fields['annotator'].queryset = project.members.filter(
            projectmembership__role='annotator'
        )