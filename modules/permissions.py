from abstracts.permissions import IsObjPublic
from common.permissions import RelatedObjPermissionProxy, IsObjOwner, partial_cls
from generic_status.permissions import HasObjRoles
from modules.models import Module


MODULE_KWARGS = dict(
    model=Module,
    lookup_url_kwarg="module_id",
)

ModuleObjIsPublic = partial_cls(
    RelatedObjPermissionProxy, decorated=IsObjPublic, **MODULE_KWARGS
)
ModuleObjIsOwner = partial_cls(
    RelatedObjPermissionProxy, decorated=IsObjOwner, **MODULE_KWARGS
)
ModuleHasViewerOrEditorRoles = partial_cls(
    RelatedObjPermissionProxy,
    decorated=partial_cls(HasObjRoles, roles=["viewer", "editor"]),
    **MODULE_KWARGS
)
