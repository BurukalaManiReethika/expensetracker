from django import forms
from django.contrib.auth.models import User
from .models import ExpenseGroup


class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = ExpenseGroup
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Goa Trip, Flatmates'
            })
        }


class AddMemberForm(forms.Form):
    username_or_email = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username or email'
        })
    )

    def clean_username_or_email(self):
        value = self.cleaned_data['username_or_email']
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=value)
            except User.DoesNotExist:
                raise forms.ValidationError("No user found with this username/email.")
        return user
