from fastapi import FastAPI
from controllers import games
from fastapi_versioning import VersionedFastAPI

app = FastAPI()


def main_config():
    configure_routers()


def configure_routers():
    app.include_router(games.router)


main_config()
app = VersionedFastAPI(app, version_format='{major}', prefix_format='/v{major}')
