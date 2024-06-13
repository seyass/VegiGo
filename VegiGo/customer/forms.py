# forms.py

from django import forms
from django.contrib.auth.forms import UserChangeForm
from authentication.models import vgUser
from .models import UserAddress,Cart,CartItem


class UserProfileForm(UserChangeForm):
    password = None  # Remove password field from the form
    class Meta:
        model = vgUser
        fields = ('first_name', 'last_name', 'email')

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ('user',)

class CartItemForm(forms.ModelForm):

    class Meta:
        model=CartItem
        fields=('quantity','cart','product')

class AddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = ['firstname', 'lastname', 'street_address', 'city', 'district', 'pincode', 'address_type','phone_number','landmark']
        widgets = {
            'firstname': forms.TextInput(attrs={
                'class': 'form-control primary-color', # CSS class for input field
                'id': 'firstname',
                'placeholder': 'Enter First Name',
            }),
            'lastname': forms.TextInput(attrs={
                'class': 'form-control primary-color',
                'id': 'lastname',
                'placeholder': 'Enter Last Name',
            }),
            'street_address': forms.TextInput(attrs={
                'class': 'form-control primary-color',
                'id': 'street_address',
                'placeholder': 'Enter Street Address',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control primary-color',
                'id': 'city',
                'placeholder': 'Enter City',
            }),
            'district': forms.Select(attrs={
                'class': 'form-control primary-color',
                'id': 'state',
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control primary-color',
                'id': 'pincode',
                'placeholder': 'Enter Pincode',
            }),
            'address_type': forms.RadioSelect(attrs={
                'class': 'form-check form-check-inline',  # Use Bootstrap's inline classes
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control primary-color',
                'id': 'phone_number',
                'placeholder': 'Enter Phone Number',
            }),
            'landmark': forms.TextInput(attrs={
                'class': 'form-control primary-color',
                'id': 'landmark',
                'placeholder': 'Enter Landmark',
            }),
        }
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if len(phone_number) < 10 or set(phone_number) == {'0'}:
            raise forms.ValidationError('Enter a valid phone number')
        
        return phone_number
    
