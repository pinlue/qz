from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema


class ToggleRelationSchema(SwaggerAutoSchema):
    def get_operation(self, operation_keys):
        operation = super().get_operation(operation_keys)
        relation_name = getattr(self.view, "relation_name", "relation")

        if self.method == 'POST':
            operation.description = f"Create a {relation_name} relation for the object."
            operation.responses = {
                201: openapi.Response(description=f"{relation_name.capitalize()} created"),
                200: openapi.Response(description=f"{relation_name.capitalize()} already exists"),
            }
        elif self.method == 'DELETE':
            operation.description = f"Remove a {relation_name} relation from the object."
            operation.responses = {
                200: openapi.Response(description=f"{relation_name.capitalize()} removed"),
            }
        return operation