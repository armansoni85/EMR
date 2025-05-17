from drf_yasg.inspectors import SwaggerAutoSchema


class CustomSchemaNoDefaultFilterView(SwaggerAutoSchema):
    """This return Swagger Schema by exluding default filter params"""

    def get_query_parameters(self):
        return []
