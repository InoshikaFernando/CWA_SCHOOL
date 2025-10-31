#!/usr/bin/env python
"""
Script to update existing Basic Facts points in session data by dividing by 10.
This updates session data stored in the database.
"""
import os
import sys
import django
import pickle
import base64

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cwa_school.settings')
django.setup()

from django.contrib.sessions.models import Session
from django.utils import timezone
import json

def update_basic_facts_points():
    """Update Basic Facts points in all sessions by dividing by 10"""
    updated_count = 0
    error_count = 0
    
    # Get all active sessions
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    total_sessions = active_sessions.count()
    
    print(f"Found {total_sessions} active sessions. Checking for Basic Facts data...")
    
    for session in active_sessions:
        try:
            session_data = session.get_decoded()
            modified = False
            
            # Check for Basic Facts results keys
            keys_to_update = []
            for key in session_data.keys():
                if key.startswith('basic_facts_results_'):
                    keys_to_update.append(key)
            
            # Update each Basic Facts results list
            for key in keys_to_update:
                results_list = session_data.get(key, [])
                if results_list and isinstance(results_list, list):
                    for result in results_list:
                        if 'points' in result and isinstance(result['points'], (int, float)):
                            # If points > 100, it's likely the old format (not divided by 10)
                            # Basic Facts points after division by 10 should typically be < 100
                            if result['points'] > 100:
                                result['points'] = result['points'] / 10
                                modified = True
                                print(f"  Updated {key}: {result['points'] * 10} -> {result['points']}")
            
            # Also check individual quiz_results for Basic Facts (level 100+)
            for key in list(session_data.keys()):
                if key.startswith('quiz_results_'):
                    # Extract level number from key format: quiz_results_{level_number}_{session_id}
                    parts = key.split('_')
                    if len(parts) >= 3:
                        try:
                            level_num = int(parts[2])
                            if level_num >= 100:  # Basic Facts level
                                result_data = session_data.get(key, {})
                                if result_data and isinstance(result_data, dict):
                                    # We'll recalculate this on next access, but mark it for update
                                    modified = True
                        except (ValueError, IndexError):
                            pass
            
            # Save updated session data
            if modified:
                # Use the session store to properly encode the data
                from django.contrib.sessions.backends.db import SessionStore
                session_store = SessionStore(session_key=session.session_key)
                # Copy all data to the store
                for key, value in session_data.items():
                    session_store[key] = value
                session_store.save()
                updated_count += 1
                print(f"✓ Updated session {session.session_key[:8]}...")
                
        except Exception as e:
            error_count += 1
            print(f"✗ Error processing session {session.session_key[:8] if session.session_key else 'N/A'}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Update complete!")
    print(f"  Total sessions checked: {total_sessions}")
    print(f"  Sessions updated: {updated_count}")
    print(f"  Errors: {error_count}")
    print(f"{'='*60}")

if __name__ == '__main__':
    update_basic_facts_points()

