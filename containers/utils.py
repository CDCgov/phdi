from fastapi import FastAPI
from pathlib import Path


def instantiate_fastapi(title, version):
    description = Path("description.md").read_text(encoding="utf-8")
    app = FastAPI(
        title=title,
        version=version,
        contact={
            "name": "CDC Public Health Data Infrastructure",
            "url": "https://cdcgov.github.io/phdi-site/",
            "email": "dmibuildingblocks@cdc.gov",
        },
        license_info={
            "name": "Creative Commons Zero v1.0 Universal",
            "url": "https://creativecommons.org/publicdomain/zero/1.0/",
        },
        description=description,
    )
    return app
