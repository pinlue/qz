from rest_framework.permissions import IsAdminUser, IsAuthenticated

from common.permissions import IsObjAdmin, IsObjOwner


LIST_POLICY = [IsAdminUser]

CREATE_POLICY = [IsAuthenticated]

RETRIEVE_POLICY = [IsAuthenticated, IsObjAdmin | IsObjOwner]

UPDATE_POLICY = RETRIEVE_POLICY

PARTIAL_UPDATE_POLICY = RETRIEVE_POLICY

DESTROY_POLICY = RETRIEVE_POLICY


POLICIES = {
    "retrieve": RETRIEVE_POLICY,
    "list": LIST_POLICY,
    "create": CREATE_POLICY,
    "update": UPDATE_POLICY,
    "partial_update": PARTIAL_UPDATE_POLICY,
    "destroy": DESTROY_POLICY,
}
