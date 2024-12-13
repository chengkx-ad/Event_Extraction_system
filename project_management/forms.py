from django import forms
from .models import Project, ProjectMembership
from django.contrib.auth.models import User

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ProjectMembershipForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='用户',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    new_username = forms.CharField(
        max_length=150,
        required=False,
        label='新用户名',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '输入新用户名'})
    )
    
    class Meta:
        model = ProjectMembership
        fields = ['user', 'new_username', 'role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'})
        } 

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='密码', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_confirm = forms.CharField(label='确认密码', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('密码不匹配')
        return password_confirm 