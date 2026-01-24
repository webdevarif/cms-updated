"""
Tests for queue services.
"""
from django.test import TestCase
from apps.queue.services import QueueService


class QueueServiceTest(TestCase):
    def test_enqueue_task(self):
        """Test task enqueueing"""
        task = QueueService.enqueue_task('test_task', args=['arg1'], kwargs={'key': 'value'})
        
        self.assertIsNotNone(task.id)
    
    def test_get_task_status(self):
        """Test getting task status"""
        task = QueueService.enqueue_task('test_task', args=['arg1'])
        status = QueueService.get_task_status(task.id)
        
        self.assertIn('status', status)
        self.assertIn('task_id', status)
    
    def test_revoke_task(self):
        """Test task revocation"""
        task = QueueService.enqueue_task('test_task', args=['arg1'], countdown=60)
        result = QueueService.revoke_task(task.id)
        
        self.assertTrue(result)
