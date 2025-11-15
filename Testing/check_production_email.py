#!/usr/bin/env python
"""
Quick script to check email configuration in production.
This script can be run directly on the production server.
"""
import os
import sys
import django

# Add parent directory to Python path so we can import Django settings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from django.conf import settings

def check_production_email():
    """Check if email is properly configured for production"""
    
    print("=" * 80)
    print("PRODUCTION EMAIL CONFIGURATION CHECK")
    print("=" * 80)
    print()
    
    issues = []
    warnings = []
    
    # Check DEBUG
    if settings.DEBUG:
        issues.append("DEBUG=True - Emails will use console backend (not sent)")
        print("[CRITICAL] DEBUG is True - emails will NOT be sent!")
        print("           Set DEBUG=False in production")
    else:
        print("[OK] DEBUG is False - SMTP will be used")
    
    print()
    
    # Check email backend
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        issues.append("Using console email backend")
        print("[CRITICAL] Using console email backend - emails will NOT be sent!")
    else:
        print(f"[OK] Using email backend: {settings.EMAIL_BACKEND}")
    
    print()
    
    # Check email settings
    print("Email Settings:")
    print("-" * 80)
    
    email_host = getattr(settings, 'EMAIL_HOST', None)
    if not email_host or email_host == 'localhost':
        issues.append("EMAIL_HOST not set or is localhost")
        print(f"[ERROR] EMAIL_HOST: {email_host or 'Not set'}")
    else:
        print(f"[OK] EMAIL_HOST: {email_host}")
    
    email_port = getattr(settings, 'EMAIL_PORT', None)
    if not email_port:
        issues.append("EMAIL_PORT not set")
        print(f"[ERROR] EMAIL_PORT: Not set")
    else:
        print(f"[OK] EMAIL_PORT: {email_port}")
    
    email_user = getattr(settings, 'EMAIL_HOST_USER', None)
    if not email_user:
        issues.append("EMAIL_HOST_USER not set")
        print(f"[ERROR] EMAIL_HOST_USER: Not set")
    else:
        print(f"[OK] EMAIL_HOST_USER: {email_user}")
    
    email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
    if not email_password:
        issues.append("EMAIL_HOST_PASSWORD not set")
        print(f"[ERROR] EMAIL_HOST_PASSWORD: Not set")
    else:
        print(f"[OK] EMAIL_HOST_PASSWORD: {'*' * len(email_password)} (set)")
    
    email_tls = getattr(settings, 'EMAIL_USE_TLS', False)
    email_ssl = getattr(settings, 'EMAIL_USE_SSL', False)
    if not email_tls and not email_ssl:
        warnings.append("EMAIL_USE_TLS and EMAIL_USE_SSL are both False")
        print(f"[WARNING] EMAIL_USE_TLS: {email_tls}, EMAIL_USE_SSL: {email_ssl}")
    else:
        print(f"[OK] EMAIL_USE_TLS: {email_tls}, EMAIL_USE_SSL: {email_ssl}")
    
    default_from = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
    if not default_from or 'local' in default_from.lower():
        warnings.append("DEFAULT_FROM_EMAIL may not be set correctly")
        print(f"[WARNING] DEFAULT_FROM_EMAIL: {default_from}")
    else:
        print(f"[OK] DEFAULT_FROM_EMAIL: {default_from}")
    
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if issues:
        print(f"[CRITICAL] Found {len(issues)} critical issue(s):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print()
        print("Email will NOT work until these issues are fixed!")
    else:
        print("[OK] No critical issues found")
    
    if warnings:
        print(f"[WARNING] Found {len(warnings)} warning(s):")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    
    if not issues and not warnings:
        print("[SUCCESS] Email configuration looks good!")
        print("         Run 'python test_email.py --test-connection' to verify SMTP connection")
    
    print("=" * 80)
    
    return len(issues) == 0

if __name__ == "__main__":
    success = check_production_email()
    sys.exit(0 if success else 1)

