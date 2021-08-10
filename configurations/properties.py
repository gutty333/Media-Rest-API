from services.properties_service import get_settings_map

external_settings = get_settings_map()

API_VERSION = 1
OK_STATUS = 200
EXTERNAL_LINK_PREFIX = "https://"
GAME_WIKI_URL = external_settings.get("gameMediaSource")
REDIS_HOST = external_settings.get("redisHost")
REDIS_PORT = external_settings.get("redisPort")