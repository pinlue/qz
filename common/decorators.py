from common.exeptions import ChainBreak
from functools import wraps


def login_required_link(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            raise ChainBreak
        return method(self, *args, **kwargs)

    return wrapper


def swagger_safe_permissions(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if getattr(self, "swagger_fake_view", False):
            return []
        return func(self, *args, **kwargs)

    return wrapper
