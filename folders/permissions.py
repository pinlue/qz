from functools import partial

from abstracts.permissions import IsPublic
from common.permissions import IsOwner, RelatedPermissionProxy
from generic_status.permissions import IsEditor, IsViewer
from modules.models import Module


NESTED_MODULE_KWARGS = dict(
    model=Module,
    lookup_url_kwarg="module_id",
)

NestedModuleIsPublic = partial(RelatedPermissionProxy, decorated=IsPublic, **NESTED_MODULE_KWARGS)
NestedModuleIsOwner = partial(RelatedPermissionProxy, decorated=IsOwner, **NESTED_MODULE_KWARGS)
NestedModuleIsEditor = partial(RelatedPermissionProxy, decorated=IsEditor, **NESTED_MODULE_KWARGS)
NestedModuleIsViewer = partial(RelatedPermissionProxy, decorated=IsViewer, **NESTED_MODULE_KWARGS)