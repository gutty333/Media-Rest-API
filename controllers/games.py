from fastapi import APIRouter, Request
from configurations.properties import API_VERSION
from services.game_service import GameParser
from fastapi_versioning import version

router = APIRouter()


@router.get("/api/games/{game_title}")
@version(API_VERSION)
def get_game_info(game_title: str, request: Request):
    report = {}
    game_parser = GameParser()

    if len(request.query_params) > 0:
        report = game_parser.get_content_info(game_title, request)
    else:
        report = game_parser.parse_game_info(game_title)

    return {
        game_title: report
    }
