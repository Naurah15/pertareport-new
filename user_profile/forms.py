from django import forms
from django.contrib.auth import get_user_model
from .models import BuyerProfile, SellerProfile
from django.core.exceptions import ValidationError 


class BuyerProfileForm(forms.ModelForm):
    class Meta:
        model = BuyerProfile
        fields = ['profile_picture', 'store_name', 'nationality']
        widgets = {
                'store_name': forms.TextInput(attrs={'class': 'border border-gray-300 p-2 rounded-md'}),
                'nationality': forms.Select(attrs={'class': 'border border-gray-300 p-2 rounded-md'}),
            }

    def __init__(self, *args, **kwargs):
        super(BuyerProfileForm, self).__init__(*args, **kwargs)
        self.fields['nationality'].widget = forms.Select()
    
    def clean_store_name(self):
        store_name = self.cleaned_data['store_name']
        if SellerProfile.objects.filter(store_name=store_name).exists() or BuyerProfile.objects.filter(store_name=store_name).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Display name already exists in another profile. Please choose a different name.")
        return store_name

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['profile_picture', 'city', 'store_name', 'subdistrict', 'village', 'address','maps']
        widgets = {
                'store_name': forms.TextInput(attrs={'class': 'border bg-white border-gray-300 p-2 rounded-md'}),
                'city': forms.TextInput(attrs={'class': 'border bg-white border-gray-300 p-2 rounded-md'}),
                'subdistrict': forms.Select(attrs={'class': 'border bg-white border-gray-300 p-2 rounded-md'}),
                'village': forms.Select(attrs={'class': 'border bg-white border-gray-300 p-2 rounded-md'}),
                'address': forms.TextInput(attrs={'class': 'border bg-white border-gray-300 p-2 rounded-md'}),
                'maps': forms.URLInput(attrs={'class': 'border bg-white border-gray-300 p-2 rounded-md'}),
            }

    def __init__(self, *args, **kwargs):
        super(SellerProfileForm, self).__init__(*args, **kwargs)
        self.fields['subdistrict'].widget = forms.Select()
        self.fields['village'].widget = forms.Select()

    def clean_store_name(self):
        store_name = self.cleaned_data['store_name']
        if BuyerProfile.objects.filter(store_name=store_name).exists() or SellerProfile.objects.filter(store_name=store_name).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Store name already exists in another profile. Please choose a different name.")
        return store_name