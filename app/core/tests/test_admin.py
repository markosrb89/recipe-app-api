from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    """Function that is run before every test that we run"""
    def setUp(self):
        """Create client for tests"""
        self.client = Client()
        """Create superuser"""
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin-test@gmail.com',
            password='AdminTest123'
        )
        """Login superuser"""
        self.client.force_login(self.admin_user)
        """Create regular user"""
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            name='Test user full name',
            password='Test123'
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        """Generates url for our list user page.
            * admin: -> app that you are going for
            * core_user_change_list -> this is url, see
            django admin documentation for the reference.
            Reverse helper function is used if url is changed in the future
            instead of hard coded it."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        """"
            Contains assertion checks if response contains a certain item
            and also checks if HTTP response is 200.
        """
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works"""
        # /admin/core/user/userId -> arguments
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
