from functools import partial

from abstracts.permissions import IsPublic
from common.permissions import IsOwner
from generic_status.permissions import IsEditor, IsViewer
from modules.models import Module


NESTED_MODULE_KWARGS = dict(
    nested=True,
    nested_model=Module,
    nested_id_kwarg="module_id",
)

NestedModuleIsPublic = partial(IsPublic, **NESTED_MODULE_KWARGS)
NestedModuleIsOwner = partial(IsOwner, **NESTED_MODULE_KWARGS)
NestedModuleIsEditor = partial(IsEditor, **NESTED_MODULE_KWARGS)
NestedModuleIsViewer = partial(IsViewer, **NESTED_MODULE_KWARGS)