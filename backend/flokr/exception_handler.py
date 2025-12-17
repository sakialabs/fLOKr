"""
Custom exception handler for more human-friendly error messages.
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled


def custom_exception_handler(exc, context):
    """Custom exception handler that makes error messages more user-friendly."""
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # If this is a throttled request, make the message more human-friendly
    if isinstance(exc, Throttled):
        wait_seconds = exc.wait
        
        if wait_seconds:
            if wait_seconds < 60:
                wait_msg = f"{int(wait_seconds)} seconds"
            elif wait_seconds < 3600:
                wait_minutes = int(wait_seconds / 60)
                wait_msg = f"{wait_minutes} minute{'s' if wait_minutes > 1 else ''}"
            else:
                wait_hours = int(wait_seconds / 3600)
                wait_msg = f"{wait_hours} hour{'s' if wait_hours > 1 else ''}"
            
            custom_message = f"Whoa, slow down! You're trying to do that too often. Please wait {wait_msg} and try again."
        else:
            custom_message = "You're doing that too often! Please wait a moment and try again."
        
        if response is not None:
            response.data = {
                'error': custom_message
            }
    
    return response
