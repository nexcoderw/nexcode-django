from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

def superuser_required(view_func):
    """
    Decorator for views that checks the user is logged in and is a superuser.
    Redirects to login page with message if not.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "❌ You must be logged in to access this page.")
            return redirect('controller:signIn')
        if not request.user.is_superuser:
            messages.error(request, "❌ Access denied: Superadmin privileges required.")
            return redirect('controller:signIn')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
