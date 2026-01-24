"""
Tests for search services.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.public.search.services import SearchService
from apps.public.search.models import SearchIndex, SearchQuery
from apps.stores.models import Store

User = get_user_model()


class SearchServiceTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store',
            owner=User.objects.create_user(
                email='test@example.com',
                password='testpass123'
            )
        )
        
        self.search_index = SearchIndex.objects.create(
            store=self.store,
            name='Main Index',
            index_name='main',
            content_types=['Post', 'Product'],
            fields={'title': {'weight': 2}, 'content': {'weight': 1}},
            facets=[
                {'field': 'type', 'label': 'Type', 'type': 'terms'},
                {'field': 'category_id', 'label': 'Category', 'type': 'terms'}
            ]
        )
    
    def test_search_with_query(self):
        """Test search with query"""
        results = SearchService.search(
            store=self.store,
            query='test',
            search_type='content'
        )
        
        self.assertIn('results', results)
        self.assertIn('facets', results)
        self.assertIn('total', results)
    
    def test_get_facets(self):
        """Test getting facets"""
        facets = SearchService.get_facets(
            store=self.store,
            search_type='content'
        )
        
        self.assertIsInstance(facets, list)
        self.assertEqual(len(facets), 2)  # Two facets configured
    
    def test_track_search(self):
        """Test search query tracking"""
        SearchService.track_search(
            store=self.store,
            query='test query',
            search_type='content',
            results_count=5,
            filters={'type': 'post'},
            duration_ms=150
        )
        
        # Verify search query was tracked
        search_query = SearchQuery.objects.filter(
            store=self.store,
            query='test query'
        ).first()
        
        self.assertIsNotNone(search_query)
        self.assertEqual(search_query.search_type, 'content')
        self.assertEqual(search_query.results_count, 5)
        self.assertEqual(search_query.duration_ms, 150)
    
    def test_index_document(self):
        """Test document indexing"""
        data = {
            'title': 'Test Page',
            'content': 'Test content',
            'url': '/test-page'
        }
        
        result = SearchService.index_document(
            store=self.store,
            document_type='Page',
            document_id='1',
            data=data
        )
        
        self.assertTrue(result)
    
    def test_get_index_name(self):
        """Test index name generation"""
        index_name = self.search_index.get_index_name()
        expected_name = f"{self.store.slug}_{self.search_index.index_name}"
        
        self.assertEqual(index_name, expected_name)
