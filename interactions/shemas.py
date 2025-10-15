from drf_spectacular.utils import extend_schema


toggle_post_schema = extend_schema(
    methods=["POST"],
    request=None,
    responses={
        201: None,
        403: None,
        404: None,
    },
)

toggle_delete_schema = extend_schema(
    methods=["DELETE"],
    request=None,
    responses={
        200: None,
        403: None,
        404: None,
    },
)
