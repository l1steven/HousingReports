import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from loginApp.models import Complaint, ComplaintFile

class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_login(self):
        response = self.client.post(reverse('account_login'), {'username': 'testuser', 'password': 'password123'})
        self.assertRedirects(response, reverse('dashboard'))

    def test_logout(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('account_logout'))
        self.assertRedirects(response, reverse('account_login'))

class ComplaintTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.complaint = Complaint.objects.create(user=self.user, name='Leaky Faucet', location='Bathroom', description='The faucet leaks.')

    def test_complaint_submission(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp_file:
            file = SimpleUploadedFile(tmp_file.name, content=b'', content_type='image/jpeg')
            response = self.client.post(reverse('complaint_form'), {
                'name': 'Broken Window',
                'location': 'Living Room',
                'description': 'The window is broken.',
                'upload': file,
            }, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(Complaint.objects.filter(name='Broken Window').exists())

    def test_anonymous_complaint_submission(self):
        response = self.client.post(reverse('anonymous_complaint_view'), {
            'name': 'Anonymous',
            'location': 'Park',
            'description': 'Graffiti all over the place.',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Complaint.objects.filter(name='Anonymous').exists())

    def test_edit_complaint(self):
        response = self.client.post(reverse('editcomplaintcommon', args=(self.complaint.id,)), {
            'name': 'Leaky Faucet Updated',
            'location': 'Bathroom',
            'description': 'The faucet leaks a lot now.',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.description, 'The faucet leaks a lot now.')

    def test_delete_complaint(self):
        response = self.client.post(reverse('deletecomplaintcommon', args=(self.complaint.id,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Complaint.objects.filter(id=self.complaint.id).exists())

'''
class AccessControlTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='password123')
        self.user2 = User.objects.create_user(username='testuser2', password='password123')
        self.client.login(username='testuser1', password='password123')
        self.complaint = Complaint.objects.create(user=self.user1, name='Noise Complaint', location='Neighbor', description='Loud music at night.')

    def test_edit_complaint_by_non_owner(self):
        self.client.logout()
        self.client.login(username='testuser2', password='password123')
        response = self.client.get(reverse('editcomplaintcommon', args=(self.complaint.id,)))
        self.assertEqual(response.status_code, 403)

    def test_delete_complaint_by_non_owner(self):
        self.client.logout()
        self.client.login(username='testuser2', password='password123')
        response = self.client.get(reverse('deletecomplaintcommon', args=(self.complaint.id,)))
        self.assertEqual(response.status_code, 403)
'''