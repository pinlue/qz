from rest_framework.permissions import IsAuthenticated, AllowAny

from abstracts.permissions import IsObjPublic
from common.permissions import IsObjAdmin, IsObjOwner, partial_cls
from generic_status.permissions import HasObjRoles


CREATE_POLICY = [IsAuthenticated]

DESTROY_POLICY = [IsAuthenticated, IsObjOwner | IsObjAdmin]

UPDATE_POLICY = [IsObjAdmin | IsObjOwner | partial_cls(HasObjRoles, roles=["editor"])]

PARTIAL_UPDATE_POLICY = UPDATE_POLICY

LIST_POLICY = [AllowAny]

RETRIEVE_POLICY = [
    IsObjAdmin
    | IsObjOwner
    | IsObjPublic
    | partial_cls(HasObjRoles, roles=["editor", "viewer"])
]

RATES_POLICY = [
    IsAuthenticated,
    ~IsObjOwner
    & (IsObjPublic | IsObjAdmin | partial_cls(HasObjRoles, roles=["viewer", "editor"])),
]

PINS_POLICY = [
    IsAuthenticated,
    IsObjPublic
    | IsObjAdmin
    | IsObjOwner
    | partial_cls(HasObjRoles, roles=["editor", "viewer"]),
]

SAVES_POLICY = PINS_POLICY

COPIES_POLICY = PINS_POLICY

MODULE_MERGE_POLICY = PINS_POLICY


POLICIES = {
    "retrieve": RETRIEVE_POLICY,
    "list": LIST_POLICY,
    "create": CREATE_POLICY,
    "update": UPDATE_POLICY,
    "partial_update": PARTIAL_UPDATE_POLICY,
    "destroy": DESTROY_POLICY,
    "saves": SAVES_POLICY,
    "pins": PINS_POLICY,
    "rates": RATES_POLICY,
    "copies": COPIES_POLICY,
}
