"""
Tests for forms API v2.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from ..models.forms import FormTemplate, FormSubmission, FormSubmissionData
from ..services import FormService

User = get_user_model()


class FormServiceTestCase(TestCase):
    """Test FormService methods"""
    
    def setUp(self):
        """Set up test data"""
        from apps.stores.models import Store
        
        self.store = Store.objects.create(
            name="Test Store",
            slug="test-store",
            owner=None
        )
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
    
    def test_create_form(self):
        """Test form creation"""
        data = {
            'title': 'Test Form',
            'slug': 'test-form',
            'description': 'Test description',
            'fields': {
                'name': {
                    'type': 'text',
                    'label': 'Name',
                    'required': True
                },
                'email': {
                    'type': 'email',
                    'label': 'Email',
                    'required': True
                }
            },
            'settings': {
                'notification_emails': ['admin@example.com']
            }
        }
        
        form = FormService.create_form(self.store, self.user, data)
        
        self.assertEqual(form.title, 'Test Form')
        self.assertEqual(form.slug, 'test-form')
        self.assertEqual(form.store, self.store)
        self.assertEqual(form.status, 'draft')
        self.assertTrue(form.save_to_database)
        self.assertTrue(form.send_email_notifications)
        self.assertEqual(len(form.form_id), 6)
        self.assertTrue(form.form_id.isdigit())
    
    def test_validate_form_data(self):
        """Test form data validation"""
        # Create form with required fields
        form = FormService.create_form(self.store, self.user, {
            'title': 'Test Form',
            'fields': {
                'name': {
                    'type': 'text',
                    'label': 'Name',
                    'required': True
                },
                'email': {
                    'type': 'email',
                    'label': 'Email',
                    'required': True
                }
            }
        })
        
        # Test valid data
        valid_data = {
            'form_data': {
                'name': 'John Doe',
                'email': 'john@example.com'
            }
        }
        result = FormService.validate_form_data(form, valid_data)
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        
        # Test missing required field
        invalid_data = {
            'form_data': {
                'name': 'John Doe'
                # Missing email
            }
        }
        result = FormService.validate_form_data(form, invalid_data)
        self.assertFalse(result['valid'])
        self.assertIn('email', result['errors'])
        
        # Test invalid email
        invalid_email_data = {
            'form_data': {
                'name': 'John Doe',
                'email': 'invalid-email'
            }
        }
        result = FormService.validate_form_data(form, invalid_email_data)
        self.assertFalse(result['valid'])
        self.assertIn('email', result['errors'])
    
    def test_process_submission(self):
        """Test form submission processing"""
        form = FormService.create_form(self.store, self.user, {
            'title': 'Test Form',
            'fields': {
                'name': {'type': 'text', 'label': 'Name'},
                'email': {'type': 'email', 'label': 'Email'}
            }
        })
        
        submission_data = {
            'form_data': {
                'name': 'John Doe',
                'email': 'john@example.com'
            },
            'ip_address': '127.0.0.1',
            'user_agent': 'Test Browser'
        }
        
        result = FormService.process_submission(
            self.store, form, submission_data, self.user
        )
        
        self.assertTrue(result['success'])
        self.assertIn('submission_id', result)
        
        # Verify submission was created
        submission = FormSubmission.objects.get(id=result['submission_id'])
        self.assertEqual(submission.form, form)
        self.assertEqual(submission.user, self.user)
        self.assertEqual(submission.ip_address, '127.0.0.1')
        
        # Verify submission data was saved
        self.assertEqual(submission.submission_data.count(), 2)
        
        name_data = submission.submission_data.get(field_name='name')
        email_data = submission.submission_data.get(field_name='email')
        
        self.assertEqual(name_data.field_value, 'John Doe')
        self.assertEqual(email_data.field_value, 'john@example.com')
    
    def test_get_form_submissions(self):
        """Test getting form submissions"""
        form = FormService.create_form(self.store, self.user, {
            'title': 'Test Form',
            'fields': {
                'name': {'type': 'text', 'label': 'Name'}
            }
        })
        
        # Create some submissions
        submission_data = {
            'form_data': {'name': 'Test User'},
            'ip_address': '127.0.0.1',
            'user_agent': 'Test Browser'
        }
        
        FormService.process_submission(self.store, form, submission_data)
        FormService.process_submission(self.store, form, submission_data)
        
        result = FormService.get_form_submissions(self.store, form.id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['form'], form)
        self.assertEqual(result['count'], 2)
        self.assertEqual(len(result['submissions']), 2)


class PublicFormAPITestCase(APITestCase):
    """Test public form API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        from apps.stores.models import Store
        
        self.store = Store.objects.create(
            name="Test Store",
            slug="test-store",
            owner=None
        )
        
        # Create a published form
        self.form = FormTemplate.objects.create(
            store=self.store,
            title="Contact Form",
            form_id="123456",
            status='published',
            is_active=True,
            fields={
                'name': {'type': 'text', 'label': 'Name', 'required': True},
                'email': {'type': 'email', 'label': 'Email', 'required': True}
            }
        )
        
        # Create a draft form (should not be visible in public API)
        self.draft_form = FormTemplate.objects.create(
            store=self.store,
            title="Draft Form",
            form_id="654321",
            status='draft',
            is_active=True,
            fields={}
        )
    
    def test_list_forms(self):
        """Test listing published forms"""
        url = reverse('forms_v2:public-forms-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only published form
        
        form_data = response.data[0]
        self.assertEqual(form_data['title'], 'Contact Form')
        self.assertEqual(form_data['form_id'], '123456')
        self.assertEqual(form_data['status'], 'published')
    
    def test_retrieve_form(self):
        """Test retrieving a form by form_id"""
        url = reverse('forms_v2:public-forms-detail', kwargs={'pk': '123456'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['form_id'], '123456')
        self.assertEqual(response.data['title'], 'Contact Form')
    
    def test_retrieve_draft_form(self):
        """Test that draft forms are not accessible"""
        url = reverse('forms_v2:public-forms-detail', kwargs={'pk': '654321'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_submit_form(self):
        """Test form submission"""
        url = reverse('forms_v2:public-forms-submit', kwargs={'pk': '123456'})
        data = {
            'form_data': {
                'name': 'Test User',
                'email': 'test@example.com'
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('submission_id', response.data)
        
        # Verify submission was created
        submission = FormSubmission.objects.get(id=response.data['submission_id'])
        self.assertEqual(submission.form, self.form)
        self.assertEqual(submission.status, 'submitted')
    
    def test_submit_form_invalid_data(self):
        """Test form submission with invalid data"""
        url = reverse('forms_v2:public-forms-submit', kwargs={'pk': '123456'})
        data = {
            'form_data': {
                'name': 'Test User'
                # Missing required email field
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
    
    def test_submit_nonexistent_form(self):
        """Test submitting to non-existent form"""
        url = reverse('forms_v2:public-forms-submit', kwargs={'pk': '999999'})
        data = {
            'form_data': {
                'name': 'Test User',
                'email': 'test@example.com'
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CustomerFormAPITestCase(APITestCase):
    """Test customer form API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        from apps.stores.models import Store
        
        self.store = Store.objects.create(
            name="Test Store",
            slug="test-store",
            owner=None
        )
        
        self.user = User.objects.create_user(
            email="customer@example.com",
            password="testpass123"
        )
        
        # Add user to store
        from apps.stores.models import StoreMember
        StoreMember.objects.create(
            store=self.store,
            user=self.user,
            role='customer'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_create_form(self):
        """Test creating a form as customer"""
        url = reverse('forms_v2:customer-forms-list')
        data = {
            'title': 'Customer Form',
            'slug': 'customer-form',
            'description': 'Created by customer',
            'fields': {
                'message': {'type': 'textarea', 'label': 'Message'}
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Customer Form')
        self.assertEqual(response.data['status'], 'draft')
    
    def test_update_form(self):
        """Test updating a form"""
        # Create form first
        form = FormTemplate.objects.create(
            store=self.store,
            title='Original Title',
            form_id='111111',
            status='draft',
            created_by=self.user
        )
        
        url = reverse('forms_v2:customer-forms-detail', kwargs={'pk': form.id})
        data = {
            'title': 'Updated Title',
            'description': 'Updated description'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')
        self.assertEqual(response.data['description'], 'Updated description')
    
    def test_delete_form(self):
        """Test deleting a form"""
        form = FormTemplate.objects.create(
            store=self.store,
            title='To Delete',
            form_id='222222',
            created_by=self.user
        )
        
        url = reverse('forms_v2:customer-forms-detail', kwargs={'pk': form.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FormTemplate.objects.filter(id=form.id).exists())


class DashboardFormAPITestCase(CustomerFormAPITestCase):
    """Test dashboard form API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        from apps.stores.models import Store, StoreMember
        
        self.store = Store.objects.create(
            name="Test Store",
            slug="test-store",
            owner=None
        )
        
        self.user = User.objects.create_user(
            email="admin@example.com",
            password="testpass123"
        )
        
        # Add user as admin
        StoreMember.objects.create(
            store=self.store,
            user=self.user,
            role='admin'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_export_submissions(self):
        """Test exporting form submissions to CSV"""
        # Create form and submissions
        form = FormTemplate.objects.create(
            store=self.store,
            title='Export Test Form',
            form_id='333333',
            status='published'
        )
        
        # Create submissions
        for i in range(3):
            submission_data = {
                'form_data': {'name': f'User {i}'},
                'ip_address': '127.0.0.1',
                'user_agent': 'Test Browser'
            }
            FormService.process_submission(self.store, form, submission_data, self.user)
        
        url = reverse('forms_v2:dashboard-forms-export', kwargs={'pk': form.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        
        # Check CSV content
        content = response.content.decode('utf-8')
        self.assertIn('Submission ID', content)
        self.assertIn('Date', content)
        self.assertIn('User', content)
        self.assertIn('Form Data', content)
        self.assertIn('User 1', content)
        self.assertIn('User 2', content)
        self.assertIn('User 3', content)
