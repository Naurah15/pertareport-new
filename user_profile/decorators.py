from django.shortcuts import render
from functools import wraps

def user_is_seller(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role == 1:  # 1 untuk seller
            return view_func(request, *args, **kwargs)
        return render(request, '403.html', status=403)
    return _wrapped_view

def user_is_buyer(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role == 0:  # 0 untuk buyer
            return view_func(request, *args, **kwargs)
        return render(request, '403.html', status=403)
    return _wrapped_view