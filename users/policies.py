from rest_framework.permissions import AllowAny, IsAuthenticated

from common.permissions import IsObjOwner, IsObjAdmin

DESTROY_POLICY = [IsAuthenticated, IsObjOwner | IsObjAdmin]

LIST_POLICY = [AllowAny]

RETRIEVE_POLICY = LIST_POLICY


POLICIES = {
    "list": LIST_POLICY,
    "retrieve": RETRIEVE_POLICY,
    "destroy": DESTROY_POLICY,
}
