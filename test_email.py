#!/usr/bin/env python
"""
Test email functionality in Django.
This script tests the email configuration and sends a test email.
"""
import os
import sys
import django
from django.conf import settings
from django.core.mail import send_mail, mail_admins, mail_managers
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

def test_email_configuration():
    """Display current email configuration"""
    print("=" * 80)
    print("EMAIL CONFIGURATION TEST")
    print("=" * 80)
    print()
    
    print("Current Settings:")
    print("-" * 80)
    print(f"DEBUG: {settings.DEBUG}")
    if settings.DEBUG:
        print("[WARNING] DEBUG=True means emails will use console backend (not sent)")
        print("          Set DEBUG=False in production to use SMTP")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
    print(f"EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', 'Not set')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set') or 'Not set'}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(getattr(settings, 'EMAIL_HOST_PASSWORD', '')) if getattr(settings, 'EMAIL_HOST_PASSWORD', '') else 'Not set'}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")
    print(f"SERVER_EMAIL: {getattr(settings, 'SERVER_EMAIL', getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set'))}")
    print()
    
    # Check environment variables
    print("Environment Variables:")
    print("-" * 80)
    print(f"EMAIL_HOST (env): {os.getenv('EMAIL_HOST', 'Not set')}")
    print(f"EMAIL_PORT (env): {os.getenv('EMAIL_PORT', 'Not set')}")
    print(f"EMAIL_HOST_USER (env): {os.getenv('EMAIL_HOST_USER', 'Not set') or 'Not set'}")
    print(f"EMAIL_HOST_PASSWORD (env): {'*' * len(os.getenv('EMAIL_HOST_PASSWORD', '')) if os.getenv('EMAIL_HOST_PASSWORD', '') else 'Not set'}")
    print(f"DEFAULT_FROM_EMAIL (env): {os.getenv('DEFAULT_FROM_EMAIL', 'Not set')}")
    print()
    
    # Check if using console backend (development)
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        print("[WARNING] Using console email backend (emails will only print to console)")
        print("   This is typically used in development mode (DEBUG=True)")
        print("   In production, set DEBUG=False to use SMTP")
        print()
    
    return settings.EMAIL_BACKEND


def test_smtp_connection():
    """Test SMTP connection without sending an email"""
    print("Testing SMTP Connection:")
    print("-" * 80)
    
    # Use environment variables directly if settings don't have them (DEBUG=True case)
    email_host = getattr(settings, 'EMAIL_HOST', None) or os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    email_port = getattr(settings, 'EMAIL_PORT', None) or int(os.getenv('EMAIL_PORT', '587'))
    email_user = getattr(settings, 'EMAIL_HOST_USER', None) or os.getenv('EMAIL_HOST_USER', '')
    email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None) or os.getenv('EMAIL_HOST_PASSWORD', '')
    email_use_tls = getattr(settings, 'EMAIL_USE_TLS', True)
    
    print(f"Using SMTP settings:")
    print(f"  Host: {email_host}")
    print(f"  Port: {email_port}")
    print(f"  User: {email_user}")
    print(f"  TLS: {email_use_tls}")
    print()
    
    try:
        backend = EmailBackend(
            host=email_host,
            port=email_port,
            username=email_user,
            password=email_password,
            use_tls=email_use_tls,
            use_ssl=False,
            fail_silently=False,
        )
        
        # Open connection
        backend.open()
        print("[OK] SMTP connection successful!")
        
        # Close connection
        backend.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] SMTP connection failed: {str(e)}")
        print()
        print("Common issues:")
        print("  - Incorrect EMAIL_HOST or EMAIL_PORT")
        print("  - Wrong EMAIL_HOST_USER or EMAIL_HOST_PASSWORD")
        print("  - EMAIL_USE_TLS/SSL not set correctly")
        print("  - Firewall blocking SMTP port")
        print("  - Gmail requires 'App Password' instead of regular password")
        return False


def send_test_email(recipient_email=None):
    """Send a test email"""
    print()
    print("=" * 80)
    print("SENDING TEST EMAIL")
    print("=" * 80)
    print()
    
    if not recipient_email:
        recipient_email = input("Enter recipient email address (or press Enter to skip): ").strip()
        if not recipient_email:
            print("Skipping test email send.")
            return False
    
    test_subject = "Test Email from CWA School"
    test_message = f"""
This is a test email from the CWA School application.

Email Configuration:
- Backend: {settings.EMAIL_BACKEND}
- Host: {getattr(settings, 'EMAIL_HOST', 'Not set')}
- Port: {getattr(settings, 'EMAIL_PORT', 'Not set')}
- From: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}

If you receive this email, your email configuration is working correctly!

Sent at: {django.utils.timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    try:
        send_mail(
            subject=test_subject,
            message=test_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        print(f"[OK] Test email sent successfully to {recipient_email}!")
        print("   Please check the recipient's inbox (and spam folder).")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to send test email: {str(e)}")
        print()
        print("Error details:")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test email functionality')
    parser.add_argument('--email', type=str, help='Email address to send test email to')
    parser.add_argument('--test-connection', action='store_true', help='Test SMTP connection only')
    parser.add_argument('--send', action='store_true', help='Send test email')
    
    args = parser.parse_args()
    
    # Show configuration
    backend = test_email_configuration()
    
    # Test connection if requested or if using SMTP
    if args.test_connection or (backend == 'django.core.mail.backends.smtp.EmailBackend' and not args.send):
        test_smtp_connection()
    
    # Send test email if requested
    if args.send or args.email:
        send_test_email(args.email)
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    print("Usage examples:")
    print("  python test_email.py                    # Show configuration only")
    print("  python test_email.py --test-connection  # Test SMTP connection")
    print("  python test_email.py --send             # Send test email (will prompt for email)")
    print("  python test_email.py --email user@example.com  # Send test email to specific address")
    print("=" * 80)


if __name__ == "__main__":
    import django.utils.timezone
    main()

