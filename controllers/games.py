import json
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi_versioning import version
from configurations.properties import API_VERSION
from services.game_service import GameParser
from services.storage_client import cache_input, check_input_cache

router = APIRouter()


@router.get("/api/games/{game_title}")
@version(API_VERSION)
def get_game_info(game_title: str, request: Request, background_task: BackgroundTasks):
    raw_request: str = str(request.url)
    cached_report = check_input_cache(raw_request)

    if cached_report:
        report: dict = json.loads(cached_report)
    else:
        game_parser = GameParser()

        if len(request.query_params) > 0:
            report = game_parser.get_content_info(game_title, request)
        else:
            report = game_parser.parse_game_info(game_title)

    # Cache client request
    background_task.add_task(cache_input, raw_request, json.dumps(report))

    return {
        game_title: report
    }
