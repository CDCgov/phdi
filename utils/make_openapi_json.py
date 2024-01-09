import json

from fastapi.openapi.utils import get_openapi

try:
    from app.main import app
except ModuleNotFoundError:
    from main import app
"""
This is a simple script that writes the OpenAPI schema for a FastAPI application to
a JSON file. This JSON can then be used with a tool like redoc-cli to generate a static
HTML version of the API documentation served by a FastAPI applications at the /docs
endpoint.
"""

with open("openapi.json", "w") as file:
    json.dump(
        get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
            license_info=app.license_info,
            contact=app.contact,
        ),
        file,
    )
