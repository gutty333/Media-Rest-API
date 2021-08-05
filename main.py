from fastapi import FastAPI
from controllers import games

app = FastAPI()


def main_config():
    configure_routers()


def configure_routers():
    app.include_router(games.router)


main_config()
