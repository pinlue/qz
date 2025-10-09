from common.exeptions import ChainBreak


def login_required_link(method):
    def wrapper(self, *args, **kwargs):
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            raise ChainBreak
        return method(self, *args, **kwargs)
    return wrapper