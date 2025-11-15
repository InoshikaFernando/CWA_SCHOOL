# Email Setup Guide for Production

## Problem
Emails are not working in production because `DEBUG=True` forces Django to use the console email backend (emails print to console instead of being sent).

## Solution

### Step 1: Set DEBUG=False in Production

In your production environment, set the `DEBUG` environment variable to `False`:

**Option A: Using .env file**
```bash
DEBUG=False
```

**Option B: Using environment variable directly**
```bash
export DEBUG=False
```

**Option C: In your hosting platform (PythonAnywhere, etc.)**
- Go to your web app settings
- Add environment variable: `DEBUG=False`

### Step 2: Verify Email Environment Variables

Make sure these are set in your production environment:

```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### Step 3: Gmail App Password Setup

If using Gmail, you **must** use an App Password, not your regular password:

1. Go to your Google Account settings
2. Enable 2-Step Verification (required for App Passwords)
3. Go to Security → App Passwords
4. Generate a new app password for "Mail"
5. Use this 16-character password as `EMAIL_HOST_PASSWORD`

### Step 4: Test Email Configuration

Run the test script in production:

```bash
# Test configuration
python test_email.py

# Test SMTP connection
python test_email.py --test-connection

# Send test email
python test_email.py --email your-email@example.com
```

## Verification Checklist

- [ ] `DEBUG=False` is set in production
- [ ] `EMAIL_HOST` is set correctly
- [ ] `EMAIL_PORT` is set (587 for TLS, 465 for SSL)
- [ ] `EMAIL_HOST_USER` is your email address
- [ ] `EMAIL_HOST_PASSWORD` is your App Password (for Gmail)
- [ ] `EMAIL_USE_TLS=True` (for port 587)
- [ ] `DEFAULT_FROM_EMAIL` is set
- [ ] SMTP connection test passes
- [ ] Test email is received

## Common Issues

### Issue: "Authentication failed"
**Solution:** 
- Use App Password instead of regular password for Gmail
- Check that 2-Step Verification is enabled

### Issue: "Connection refused"
**Solution:**
- Check firewall settings
- Verify EMAIL_HOST and EMAIL_PORT are correct
- Try port 465 with SSL instead of 587 with TLS

### Issue: "Emails still not sending"
**Solution:**
- Verify `DEBUG=False` in production
- Check that environment variables are loaded
- Restart your web server after changing environment variables

## Testing in Production

After making changes:

1. **Restart your web server** (required for environment variable changes)
2. **Test password reset** - try the "Forgot password" feature
3. **Check logs** - look for email errors in your server logs
4. **Run test script** - use `test_email.py` to verify configuration

## Security Notes

- Never commit `.env` file with passwords to git
- Use App Passwords for Gmail (more secure)
- Consider using a dedicated email service (SendGrid, Mailgun) for production
- Rotate passwords regularly

