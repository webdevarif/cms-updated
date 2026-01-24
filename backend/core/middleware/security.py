"""
Security middleware for Digital Farmers CMS.

This middleware handles various security-related aspects of the application,
including request validation, security headers, and protection against
common web vulnerabilities.
"""
import re
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.middleware.clickjacking import XFrameOptionsMiddleware
from django.middleware.security import SecurityMiddleware as DjangoSecurityMiddleware

class SecurityMiddleware(DjangoSecurityMiddleware, MiddlewareMixin):
    """
    Enhanced security middleware that extends Django's built-in security middleware
    with additional security headers and protections.
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        # List of allowed hosts for the X-Forwarded-Host header
        self.allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        
        # Compile regex for allowed hosts for better performance
        self.allowed_hosts_regex = [
            re.compile(r'^%s$' % re.escape(host).replace('\*', r'[^.]*')) 
            for host in self.allowed_hosts if '*' in host
        ]
    
    def process_request(self, request):
        """
        Process the request before it reaches the view.
        """
        # Call parent's process_request
        response = super().process_request(request)
        
        # Add security headers
        if not hasattr(self, 'process_response'):
            # For older versions of Django that don't use process_response
            response = self.get_response(request)
            response = self.process_response(request, response)
        
        return response or self.get_response(request)
    
    def process_response(self, request, response):
        """
        Process the response before it's sent to the client.
        """
        # Call parent's process_response first
        response = super().process_response(request, response)
        
        # Add additional security headers
        self._add_security_headers(request, response)
        
        return response
    
    def _add_security_headers(self, request, response):
        """
        Add security-related headers to the response.
        """
        # Content Security Policy (CSP)
        if not response.get('Content-Security-Policy', ''):
            csp = "default-src 'self'; " \
                  "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; " \
                  "style-src 'self' 'unsafe-inline' https:; " \
                  "img-src 'self' data: https:; " \
                  "font-src 'self' https: data:; " \
                  "connect-src 'self' https:; " \
                  "frame-ancestors 'self'; " \
                  "form-action 'self'; "
            response['Content-Security-Policy'] = csp
        
        # X-Content-Type-Options
        if not response.get('X-Content-Type-Options', ''):
            response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options (already handled by parent, but we can override if needed)
        if not response.get('X-Frame-Options', ''):
            response['X-Frame-Options'] = 'SAMEORIGIN'
        
        # X-XSS-Protection
        if not response.get('X-XSS-Protection', ''):
            response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer-Policy
        if not response.get('Referrer-Policy', ''):
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature-Policy
        if not response.get('Feature-Policy', ''):
            response['Feature-Policy'] = "geolocation 'none'; microphone 'none'; camera 'none'"
