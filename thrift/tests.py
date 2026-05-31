from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import CartItem, Product


class AddToCartTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.buyer = User.objects.create_user(
            email='buyer@example.com',
            password='testpass123',
            phone_number='1111111111',
        )
        self.seller = User.objects.create_user(
            email='seller@example.com',
            password='testpass123',
            phone_number='2222222222',
        )
        self.product = Product.objects.create(
            seller=self.seller,
            title='Denim Jacket',
            description='A lightly used jacket.',
            price='500.00',
            condition='good',
            category='clothes',
        )

    def test_add_to_cart_creates_cart_item(self):
        self.client.login(email='buyer@example.com', password='testpass123')

        response = self.client.post(reverse('add_to_cart', args=[self.product.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(CartItem.objects.filter(cart__user=self.buyer, product=self.product).count(), 1)

    def test_add_to_cart_does_not_duplicate_existing_item(self):
        self.client.login(email='buyer@example.com', password='testpass123')

        self.client.post(reverse('add_to_cart', args=[self.product.id]))
        response = self.client.post(reverse('add_to_cart', args=[self.product.id]))

        self.assertEqual(response.status_code, 200)
        self.assertIn('already in your cart', response.json()['message'])
        self.assertEqual(CartItem.objects.filter(cart__user=self.buyer, product=self.product).count(), 1)

    def test_add_to_cart_rejects_sold_item(self):
        self.client.login(email='buyer@example.com', password='testpass123')
        self.product.status = 'sold'
        self.product.save()

        response = self.client.post(reverse('add_to_cart', args=[self.product.id]))

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertEqual(CartItem.objects.count(), 0)

    def test_add_to_cart_rejects_own_product(self):
        self.client.login(email='seller@example.com', password='testpass123')

        response = self.client.post(reverse('add_to_cart', args=[self.product.id]))

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertEqual(CartItem.objects.count(), 0)

    def test_remove_from_cart_deletes_cart_item(self):
        self.client.login(email='buyer@example.com', password='testpass123')
        self.client.post(reverse('add_to_cart', args=[self.product.id]))
        cart_item = CartItem.objects.get(cart__user=self.buyer, product=self.product)

        response = self.client.post(reverse('remove_from_cart', args=[cart_item.id]))

        self.assertRedirects(response, reverse('cart'))
        self.assertEqual(CartItem.objects.count(), 0)
