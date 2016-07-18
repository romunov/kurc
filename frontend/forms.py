from django import forms
from django.contrib.auth.models import User
from frontend.models import UserAddress


class BasicUserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }


class UserAddressSettingsForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = ['street', 'post_name', 'post_number']
        widgets = {
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'post_name': forms.TextInput(attrs={'class': 'form-control'}),
            'post_number': forms.NumberInput(attrs={'class': 'form-control'})
        }
