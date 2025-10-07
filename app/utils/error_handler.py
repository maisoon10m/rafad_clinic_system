"""
Error handling utilities for Rafad Clinic System
"""
from flask import flash, current_app, request
import traceback
from datetime import datetime
import os
import json

class ErrorHandler:
    """
    Helper class for handling errors consistently across the application
    """
    
    @staticmethod
    def log_error(error, context=None):
        """
        Log an error to both the Flask logger and an error log file
        
        Args:
            error: The exception that occurred
            context: Additional context information (dict)
        """
        # Format traceback
        tb = traceback.format_exc()
        
        # Get error info
        error_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': tb,
            'endpoint': request.endpoint if request else None,
            'url': request.url if request else None,
            'method': request.method if request else None,
            'user_agent': str(request.user_agent) if request and request.user_agent else None,
            'context': context
        }
        
        # Log to Flask logger
        error_log_message = f"Error: {error_info['error_type']} - {error_info['error_message']}"
        if context:
            error_log_message += f" - Context: {context}"
        current_app.logger.error(error_log_message)
        current_app.logger.error(tb)
        
        # Log to file
        try:
            log_dir = os.path.join(current_app.instance_path, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, f'errors_{datetime.utcnow().strftime("%Y-%m-%d")}.log')
            
            with open(log_file, 'a') as f:
                f.write(f"\n\n--- ERROR LOG ENTRY {error_info['timestamp']} ---\n")
                f.write(json.dumps(error_info, indent=2, default=str))
                f.write("\n--- END ERROR LOG ENTRY ---\n")
        except Exception as e:
            current_app.logger.error(f"Failed to write to error log file: {e}")
    
    @staticmethod
    def handle_error(error, user_message=None, category='danger', context=None, log=True):
        """
        Handle an error by logging it and flashing a message to the user
        
        Args:
            error: The exception that occurred
            user_message: Message to display to the user (defaults to generic message)
            category: Flash message category ('danger', 'warning', etc.)
            context: Additional context information (dict)
            log: Whether to log the error (default: True)
            
        Returns:
            None
        """
        if log:
            ErrorHandler.log_error(error, context)
        
        if user_message is None:
            if current_app.debug:
                # In debug mode, show the actual error
                user_message = f"An error occurred: {str(error)}"
            else:
                # In production, show a generic message
                user_message = "An unexpected error occurred. Please try again later."
        
        flash(user_message, category)
        
    @staticmethod
    def api_error_response(error, status_code=500, user_message=None, context=None, log=True):
        """
        Handle an API error by logging it and returning a JSON response
        
        Args:
            error: The exception that occurred
            status_code: HTTP status code to return
            user_message: Message to return to the user (defaults to generic message)
            context: Additional context information (dict)
            log: Whether to log the error (default: True)
            
        Returns:
            tuple: (response_dict, status_code)
        """
        if log:
            ErrorHandler.log_error(error, context)
        
        if user_message is None:
            if current_app.debug:
                # In debug mode, show the actual error
                user_message = f"An error occurred: {str(error)}"
            else:
                # In production, show a generic message
                user_message = "An unexpected error occurred. Please try again later."
        
        response = {
            'status': 'error',
            'message': user_message
        }
        
        # Include error details in debug mode
        if current_app.debug:
            response['error'] = {
                'type': type(error).__name__,
                'message': str(error),
                'traceback': traceback.format_exc()
            }
        
        return response, status_code