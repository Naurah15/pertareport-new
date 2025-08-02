from django.test import TestCase
from django.contrib.auth.models import User
from katalog.models import Product
from .models import ReviewEntry

class ReviewEntryTests(TestCase):
    def setUp(self):
        # Buat pengguna dan produk untuk digunakan dalam pengujian
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.product = Product.objects.create(nama='Test Product', harga=10000)  # Pastikan harga ada

    def test_add_review(self):
        # Tes untuk menambahkan review
        review = ReviewEntry.objects.create(
            user=self.user,
            product=self.product,
            review_text='This is a test review.'
        )
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.review_text, 'This is a test review.')

    def test_review_str(self):
        # Tes untuk string representation dari review
        review = ReviewEntry.objects.create(
            user=self.user,
            product=self.product,
            review_text='This is a test review.'
        )
        self.assertEqual(str(review), 'testuser - Test Product')

    def test_review_time(self):
        # Tes untuk memastikan waktu review di-set dengan benar
        review = ReviewEntry.objects.create(
            user=self.user,
            product=self.product,
            review_text='This is a test review.'
        )
        self.assertIsNotNone(review.time)