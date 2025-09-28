"""
Utility functions for Rafad Clinic System
"""

def format_date(date_obj):
    """Format date to a human-readable string"""
    if not date_obj:
        return ""
    return date_obj.strftime('%Y-%m-%d')


def format_time(time_obj):
    """Format time to a human-readable string"""
    if not time_obj:
        return ""
    return time_obj.strftime('%H:%M')