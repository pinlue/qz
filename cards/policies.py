from rest_framework.permissions import IsAuthenticated

from common.permissions import IsObjAdmin, partial_cls, RelatedObjPermissionProxy
from generic_status.permissions import HasObjRoles
from modules.models import Module
from modules.permissions import (
    ModuleObjIsOwner,
    ModuleObjIsPublic,
    ModuleHasViewerOrEditorRoles,
)

RETRIEVE_POLICY = [
    ModuleObjIsPublic | IsObjAdmin | ModuleObjIsOwner | ModuleHasViewerOrEditorRoles
]

LIST_POLICY = RETRIEVE_POLICY

LEARNS_POLICY = RETRIEVE_POLICY

SAVES_POLICY = RETRIEVE_POLICY.append(IsAuthenticated)

CREATE_POLICY = [
    IsAuthenticated,
    ModuleObjIsOwner
    | partial_cls(
        RelatedObjPermissionProxy,
        decorated=partial_cls(HasObjRoles, roles=["editor"]),
        model=Module,
        lookup_url_kwarg="module_pk",
    )
    | IsObjAdmin,
]

UPDATE_POLICY = CREATE_POLICY

PARTIAL_UPDATE_POLICY = CREATE_POLICY

DESTROY_POLICY = CREATE_POLICY

POLICIES = {
    "retrieve": RETRIEVE_POLICY,
    "list": LIST_POLICY,
    "learns": LEARNS_POLICY,
    "saves": SAVES_POLICY,
    "create": CREATE_POLICY,
    "update": UPDATE_POLICY,
    "partial_update": PARTIAL_UPDATE_POLICY,
    "destroy": DESTROY_POLICY,
}