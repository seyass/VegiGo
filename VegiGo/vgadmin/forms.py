from django import forms
from .models import Branches,Coupon
from django.utils.timezone import now


class BranchesForm(forms.ModelForm):

    class Meta:
        model = Branches
        fields = ['name']

        labels = {
            'name': 'Branch Name',
        }

        # Use the widgets attribute to specify Bootstrap classes
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter branch name'}),
            
        }

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_amount', 'start_date', 'end_date', 'minimum_purchase']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Iterate through each field and apply Bootstrap classes and custom colors
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',  # Apply Bootstrap class
                'style': 'border-color: #7755A2; color: black;'  # Custom colors
            })
        
        # Customize the start_date and end_date fields to use date input type
        self.fields['start_date'].widget = forms.DateInput(attrs={
            'type': 'date',  # Specify input type as date
            'class': 'form-control',  # Bootstrap class
            'style': 'border-color: #7755A2; color: black;'  # Custom colors
        })
        
        self.fields['end_date'].widget = forms.DateInput(attrs={
            'type': 'date',  # Specify input type as date
            'class': 'form-control',  # Bootstrap class
            'style': 'border-color: #7755A2; color: black;'  # Custom colors
        })
    def clean(self):
        cleaned_data = super().clean()
        coupon_amount_check(self)

def coupon_amount_check(form):
    discount_amount = form.cleaned_data.get('discount_amount')
    minimum_purchase = form.cleaned_data.get('minimum_purchase')
    start_date = form.cleaned_data.get('start_date')
    end_date = form.cleaned_data.get('end_date')

    if start_date and end_date and start_date > end_date:
        form.add_error('start_date', 'Start date should be less than end date')

    if discount_amount is not None and discount_amount < 1:
        form.add_error('discount_amount', 'Discount amount should be greater than 0')

    if minimum_purchase is not None and minimum_purchase < 1:
        form.add_error('minimum_purchase', 'Minimum amount should be greater than 1')

    if minimum_purchase is not None and discount_amount is not None and minimum_purchase < discount_amount:
        form.add_error('minimum_purchase', 'Minimum amount should be greater than discount amount')
    if end_date and end_date < now().date():
        form.add_error('end_date', 'The selected date range is already expired')
