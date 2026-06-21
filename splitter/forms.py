from django import forms
from django.contrib.auth.models import User
from .models import ExpenseGroup

# Add at top
from django.contrib.auth.forms import UserCreationForm

# Add this class
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'Email'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
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
# Add these imports at top if not already there
from django.contrib.auth.models import User
from .models import ExpenseGroup, Expense

# ... existing GroupCreateForm, AddMemberForm stay as-is ...

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'split_type']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Dinner, Hotel, Cab'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total amount',
                'step': '0.01'
            }),
            'split_type': forms.Select(attrs={'class': 'form-select'}),
        }

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
