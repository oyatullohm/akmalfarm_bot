from django.shortcuts import  redirect
from functools import wraps

def is_login(fun):
    @wraps(fun)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return fun(request, *args, **kwargs)
        return redirect( '/login/')
    return wrapper

