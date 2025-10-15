from drf_spectacular.utils import extend_schema


def post_relation_schema(serializer):
    return extend_schema(
        methods=["POST"],
        request=serializer,
        responses={
            201: None,
            200: None,
        },
    )


def delete_relation_schema():
    return extend_schema(
        methods=["DELETE"],
        responses={
            204: None,
            404: None,
        },
    )
