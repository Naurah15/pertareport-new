from django.test import TestCase
from .forms import BuyerProfileForm, SellerProfileForm
from .models import BuyerProfile, SellerProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class BuyerProfileFormTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='buyeruser', password='testpassword')
        self.valid_data = {
            'profile_picture': 'https://example.com/image.jpg',
            'store_name': 'UniqueStore',
            'nationality': 'American'
        }

    def test_buyer_profile_form_valid(self):
        form = BuyerProfileForm(data=self.valid_data, instance=BuyerProfile(user=self.user))
        self.assertTrue(form.is_valid())

    def test_buyer_profile_form_invalid_store_name(self):
        BuyerProfile.objects.create(user=self.user, store_name='ExistingStore')
        self.valid_data['store_name'] = 'ExistingStore'
        form = BuyerProfileForm(data=self.valid_data, instance=BuyerProfile(user=self.user))
        self.assertFalse(form.is_valid())
        self.assertIn('store_name', form.errors)

    def test_buyer_profile_form_saves_correctly(self):
        form = BuyerProfileForm(data=self.valid_data, instance=BuyerProfile(user=self.user))
        if form.is_valid():
            profile = form.save()
            self.assertEqual(profile.store_name, 'UniqueStore')
            self.assertEqual(profile.user, self.user)

class SellerProfileFormTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='selleruser', password='testpassword')
        self.valid_data = {
            'profile_picture': 'https://example.com/image.jpg',
            'store_name': 'UniqueSellerStore',
            'city': 'Denpasar',
            'subdistrict': 'Denpasar Selatan',
            'village': 'Panjer',
            'address': '123 Street Name',
            'maps': 'https://www.google.com/maps'
        }

    def test_seller_profile_form_valid(self):
        form = SellerProfileForm(data=self.valid_data, instance=SellerProfile(user=self.user))
        self.assertTrue(form.is_valid())

    def test_seller_profile_form_invalid_store_name(self):
        SellerProfile.objects.create(user=self.user, store_name='ExistingSellerStore')
        self.valid_data['store_name'] = 'ExistingSellerStore'
        form = SellerProfileForm(data=self.valid_data, instance=SellerProfile(user=self.user))
        self.assertFalse(form.is_valid())
        self.assertIn('store_name', form.errors)

    def test_seller_profile_form_saves_correctly(self):
        form = SellerProfileForm(data=self.valid_data, instance=SellerProfile(user=self.user))
        if form.is_valid():
            profile = form.save()
            self.assertEqual(profile.store_name, 'UniqueSellerStore')
            self.assertEqual(profile.user, self.user)
