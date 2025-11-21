from __future__ import annotations
from typing import TYPE_CHECKING

from django.db.models import Q

from common.exeptions import ChainBreak

if TYPE_CHECKING:
    from rest_framework.request import Request
    from typing import Optional, Any


class AccessibleChain:
    def __init__(
        self,
        request: Request = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.request: Request = request
        self.next_link: AccessibleChain | None = None

    def add(self, link: "AccessibleChain") -> None:
        if self.next_link:
            self.next_link.add(link)
        else:
            self.next_link = link

    def handle(self, q: Optional[Q] = None) -> Q:
        if q is None:
            q = Q()

        if self.next_link:
            try:
                self.next_link.request = self.request
                q = self.next_link.handle(q)
            except ChainBreak:
                return q
        return q
