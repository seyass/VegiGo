# forms.py
from django import forms
from decimal import Decimal
from .models import Category, Product ,ProductLocations,Review,CategoryOffer,ProductOffer,SecondaryImage
from vgadmin.models import Branches
import json

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class ProductLocationForm(forms.ModelForm):

    class Meta:
        model = ProductLocations
        fields = ['location','quantity']
        
class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'selling_price', 'primary_image', 'unit_type']
        # Add your other form fields as needed
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'primary_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'unit_type': forms.Select(attrs={'class': 'form-control'}),
        }
    def clean_selling_price(self):
        """
        Ensure that selling_price is converted to a decimal number.
        """
        selling_price = self.cleaned_data['selling_price']
        # Convert integer value to decimal
        if isinstance(selling_price, int):
            selling_price = Decimal(selling_price)
        return selling_price
    
    def save(self, commit=True):
        # Convert integer value to decimal before saving
        instance = super().save(commit=False)
        instance.selling_price = self.clean_selling_price()
        if commit:
            instance.save()
        return instance
    
    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        selling_price = cleaned_data.get('selling_price')

        if price is not None and selling_price is not None:
            if price < 1:
                self.add_error('price', 'Enter a valid price')
            if selling_price < 1:
                self.add_error('selling_price', 'Enter a valid selling price')
            if price < selling_price:
                self.add_error('selling_price', 'Selling price cannot be greater than the original price')

        return cleaned_data

class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    # Customize the rating field to use a dropdown
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.Select(), required=True)


    class Meta:
        model = Review
        fields = ['rating','content']

class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffer
        fields = ['category', 'discount', 'description', 'start_date', 'end_date']
        labels = {
            'category': 'Category',
            'discount': 'Discount (%)',
            'description': 'Description',
            'start_date': 'Start Date',
            'end_date': 'End Date',
        }
        # Use Bootstrap form-control class and HTML5 date inputs for date fields
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control','rows':2}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        if discount < 1:
            raise forms.ValidationError('Discount should be greater than 0')
        return discount

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError({
                'start_date': 'Start date should be less than end date',
            })

        return cleaned_data

class ProductOfferForm(forms.ModelForm):

    class Meta:
        model = ProductOffer
        fields = ['product', 'discount', 'description', 'start_date', 'end_date']
        labels = {
            'product': 'Product',
            'discount': 'Discount (%)',
            'description': 'Description',
            'start_date': 'Start Date',
            'end_date': 'End Date',
        }
        # Use Bootstrap form-control class and HTML5 date inputs for date fields
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control','rows':3}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True)


    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        if discount < 1:
            raise forms.ValidationError('Discount should be greater than 0')
        return discount

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError({
                'start_date': 'Start date should be less than end date',
            })

        return cleaned_data
    


