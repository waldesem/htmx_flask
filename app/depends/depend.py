from functools import wraps

from flask import redirect, session


def login_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session.get("user"):
                return func(*args, **kwargs)
            return redirect("/auth")

        return wrapper

    return decorator


def roles_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = session.get("user")
            if user:
                if user.get("role") in roles:
                    return func(*args, **kwargs)
                return redirect("/auth")
            return redirect("/auth")

        return wrapper

    return decorator
