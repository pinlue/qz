from rest_framework.permissions import IsAuthenticated, AllowAny

from abstracts.permissions import IsObjPublic
from common.permissions import IsObjAdmin, IsObjOwner
from modules.permissions import (
    ModuleObjIsPublic,
    ModuleObjIsOwner,
    ModuleHasViewerOrEditorRoles,
)

CREATE_POLICY = [IsAuthenticated]

UPDATE_POLICY = [IsAuthenticated, IsObjAdmin | IsObjOwner]

PARTIAL_UPDATE_POLICY = UPDATE_POLICY

DESTROY_POLICY = UPDATE_POLICY

LIST_POLICY = [AllowAny]

RETRIEVE_POLICY = [IsObjAdmin | IsObjOwner | IsObjPublic]

PINS_POLICY = [IsAuthenticated, IsObjAdmin | IsObjOwner | IsObjPublic]

SAVES_POLICY = PINS_POLICY

MANAGE_MODULE_POLICY = [
    (
        IsObjAdmin
        | (
            IsObjOwner
            & (
                ModuleObjIsPublic
                | ModuleObjIsOwner
                | ModuleHasViewerOrEditorRoles
            )
        )
    )
]


POLICIES = {
    "retrieve": RETRIEVE_POLICY,
    "list": LIST_POLICY,
    "create": CREATE_POLICY,
    "update": UPDATE_POLICY,
    "partial_update": PARTIAL_UPDATE_POLICY,
    "destroy": DESTROY_POLICY,
    "saves": SAVES_POLICY,
    "pins": PINS_POLICY,
    "manage_module": MANAGE_MODULE_POLICY,
}
