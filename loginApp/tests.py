import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from loginApp.models import Complaint, ComplaintFile

'''
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
'''
        

class ComplaintTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='test@example.com')
        self.complaint = Complaint.objects.create(user=self.user, name='Leakage', location='Bice', description='Water leaking from ceiling.')

    def test_complaint_submission(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('complaint_form'), {
            'name': 'Noise',
            'location': 'Lambeth',
            'description': 'Loud noises at night.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('complaint_success'))

    def test_anonymous_complaint_submission(self):
        response = self.client.post(reverse('anonymous_complaint_form'), {
            'name': 'Anonymous',
            'location': 'JPA',
            'description': 'Graffiti all over the place.',
        }, follow=True)
        self.assertEqual(response.status_code, 302)

    def test_edit_complaint(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('edit_complaint', args=[self.complaint.id]), {
            'name': 'Updated Name',
            'location': 'Updated Location',
            'description': 'Updated description.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('complaint_success'))

    def test_delete_complaint(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('delete_complaint', args=[self.complaint.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
        
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