from django.db.models import Q

from common.exeptions import ChainBreak


class AccessibleChain:
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.next_link = None

    def add(self, link):
        if self.next_link:
            self.next_link.add(link)
        else:
            self.next_link = link

    def handle(self, q=None):
        if q is None:
            q = Q()

        if self.next_link:
            try:
                self.next_link.request = self.request
                q = self.next_link.handle(q)
            except ChainBreak:
                return q
        return q
